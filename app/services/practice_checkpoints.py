"""LangGraph checkpoints in the application transaction (SQLite or Postgres)."""
import asyncio
import base64
import hashlib
import json
from langgraph.checkpoint.base import BaseCheckpointSaver,CheckpointTuple,WRITES_IDX_MAP
from sqlalchemy import select
from app.db.models import PracticeCheckpoint


class TransactionalSaver(BaseCheckpointSaver):
    def __init__(self,session):
        super().__init__()
        self.session=session
        self.lock=asyncio.Lock()
    def encode(self,value):
        kind,data=self.serde.dumps_typed(value)
        return json.dumps([kind,base64.b64encode(data).decode()])
    def decode(self,value):
        kind,data=json.loads(value)
        return self.serde.loads_typed((kind,base64.b64decode(data)))
    def key(self,thread,ns,cid):
        return hashlib.sha256(json.dumps([thread,ns,cid]).encode()).hexdigest()
    async def aget_tuple(self,config):
        cfg=config['configurable'];thread=cfg['thread_id'];ns=cfg.get('checkpoint_ns','')
        async with self.lock:
            stmt=select(PracticeCheckpoint).where(PracticeCheckpoint.thread_id==thread,PracticeCheckpoint.namespace==ns)
            if cfg.get('checkpoint_id'):stmt=stmt.where(PracticeCheckpoint.checkpoint_id==cfg['checkpoint_id'])
            row=await self.session.scalar(stmt.order_by(PracticeCheckpoint.checkpoint_id.desc()).limit(1))
            if row is None:return None
            current={'configurable':{'thread_id':thread,'checkpoint_ns':ns,'checkpoint_id':row.checkpoint_id}}
            parent={'configurable':{'thread_id':thread,'checkpoint_ns':ns,'checkpoint_id':row.parent_id}} if row.parent_id else None
            writes=[(v[0],v[1],self.decode(v[2])) for v in json.loads(row.writes_json).values()]
            return CheckpointTuple(current,self.decode(row.checkpoint_data),self.decode(row.metadata_data),parent,writes)
    async def aput(self,config,checkpoint,metadata,new_versions):
        cfg=config['configurable'];thread=cfg['thread_id'];ns=cfg.get('checkpoint_ns','');cid=checkpoint['id']
        async with self.lock:
            self.session.add(PracticeCheckpoint(id=self.key(thread,ns,cid),thread_id=thread,namespace=ns,
                checkpoint_id=cid,parent_id=cfg.get('checkpoint_id',''),checkpoint_data=self.encode(checkpoint),
                metadata_data=self.encode(metadata),writes_json='{}'))
            await self.session.flush()
        return {'configurable':{'thread_id':thread,'checkpoint_ns':ns,'checkpoint_id':cid}}
    async def aput_writes(self,config,writes,task_id,task_path=''):
        cfg=config['configurable']
        async with self.lock:
            row=await self.session.get(PracticeCheckpoint,self.key(cfg['thread_id'],cfg.get('checkpoint_ns',''),cfg['checkpoint_id']))
            if row is None:raise RuntimeError('Missing checkpoint for pending writes')
            current=json.loads(row.writes_json)
            for i,(channel,value) in enumerate(writes):
                idx=WRITES_IDX_MAP.get(channel,i)
                key=json.dumps([task_id,idx])
                if key in current and idx>=0:continue
                current[key]=[task_id,channel,self.encode(value)]
            row.writes_json=json.dumps(current)
            await self.session.flush()

# Student profile summary pilot

Status: implemented summary, 9 November 2026. This is a view of existing evidence, not a new mastery rule.

`GET /study/profile-overview` returns section measures for each currently accessible language, plus counts of the student's own pathway records. It makes one authenticated API call. The Language Path measure is labelled **Current path checkpoints** because the existing `complete`/`mastered` calculation has not yet adopted the proposed independent transfer rule. DSA reports unique solved problems per language. Design Patterns shows reference availability and no assessed completion. The view does not add these unlike measures into a single mastery number or count a shared concept twice.

Record counts remain visible after a language entitlement expires; new learning activity still requires current access. The profile export and erasure include student pathway records. This summary does not yet provide a full historical per-section transcript, a reviewed Design Patterns pathway, AI tutor outcome metrics, or section-specific entitlements. Those require the later curriculum, tutor-evaluation, and access gates.

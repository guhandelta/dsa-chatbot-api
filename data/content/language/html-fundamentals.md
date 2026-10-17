---
track: language
difficulty: Easy
language: html
category: Fundamentals
source: authored
io_mode: function
---
# HTML fundamentals — Easy — Fundamentals

- **Role and Architecture:** HTML (HyperText Markup Language) defines the structure and semantic meaning of web documents. The authoritative specification is the WHATWG HTML Living Standard.
- **Document Structure:** Every HTML5 document begins with `<!DOCTYPE html>`, followed by the root `<html lang="en">` element containing `<head>` (metadata, character encoding, title, viewport, stylesheets) and `<body>` (rendered content).
- **Semantics:** Prefer semantic elements (`<main>`, `<nav>`, `<header>`, `<footer>`, `<article>`, `<section>`, `<aside>`) over generic `<div>` and `<span>` tags. Semantics provide out-of-the-box accessibility (a11y) tree structure and landmarks for screen readers without requiring custom ARIA attributes.
- **Text & Hierarchy:** Heading levels (`<h1>` through `<h6>`) form an accessible document outline; use exactly one `<h1>` per page. Use `<p>` for paragraphs, `<ul>`/`<ol>` with `<li>` for lists, `<strong>` for importance, and `<em>` for stress emphasis.
- **Links and Navigation:** The `<a>` element creates hyperlinks with `href`. Use `rel="noopener noreferrer"` for external targets (`target="_blank"`) to protect window context and prevent reverse tabnabbing.
- **Media and Embedding:** Images use `<img src="..." alt="...">`. The `alt` attribute is mandatory for accessibility. Use `<picture>`, `<source>`, and `srcset` for responsive images, and `<video>`/`<audio>` with `<track>` for subtitles and captions.
- **Forms and Input:** Forms use `<form action="..." method="...">` with controls (`<input>`, `<textarea>`, `<select>`, `<button>`). Every input control must be associated with a `<label for="...">` or wrapped inside a `<label>` for accessibility and hit-target expansion.
- **Attributes and Global Model:** Global attributes (`id`, `class`, `title`, `data-*`, `hidden`, `tabindex`, `contenteditable`) apply to all HTML elements. `id` must be unique per document.
- **DOM and Living Standard:** The browser parses HTML tokens into a tree of DOM nodes (`Document`, `Element`, `Text`). Malformed HTML undergoes standard error recovery according to the WHATWG parsing algorithm.

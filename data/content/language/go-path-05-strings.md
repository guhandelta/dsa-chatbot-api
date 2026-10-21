---
track: language
language: go
level: beginner
order: 5
prerequisites: go-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: countVowels
starter_code: "func countVowels(text string) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# Go: Strings and iteration — Easy — Shared curriculum

## Learn
A Go `string` is an immutable sequence of bytes, usually UTF-8 text. `len(s)` is the number of bytes, `s[i]` is a `byte`, and `for i, r := range s` decodes UTF-8 into runes while `i` is the byte offset where each rune starts. A character literal such as `'a'` is an untyped rune constant that can be compared with a byte. This exercise restricts the input to lowercase English letters, so every character is exactly one byte and indexing bytes is safe. Contract: `countVowels(text string) int` counts the letters a, e, i, o, u in text (0 to 1000 characters) and returns the count; the empty string gives 0.

## Common misconception
`len` is not a character count: `len("héllo")` is 6 because é takes two bytes. That is why the problem states the allowed alphabet, so byte indexing is valid here. Also remember that `s[i]` is a byte, so `s[i] == "a"` does not compile (a byte cannot be compared with a string); compare with the rune literal `'a'`. Do not read index `len(text)`: the last valid index is `len(text) - 1`.

## Worked example
```go
word := "héllo"
size := len(word)
fmt.Println(size)
for i, r := range word {
	fmt.Println(i, string(r))
}
```

size is 6 because é takes two bytes. The loop prints the byte offsets 0, 1, 3, 4, 5 with the characters h, é, l, l, o: after the two-byte é the next rune starts at offset 3. Byte indexing and rune iteration only agree for ASCII text.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```go
func countVowels(text string) int {
	// Write your solution here.
	return 0
}
```

## Approach
Visit every byte, add one to a counter for each of the five vowels, and return the counter. An empty string gives 0 without special handling.

## Solutions
### Go
```go
func countVowels(text string) int {
	count := 0
	for i := 0; i < len(text); i++ {
		switch text[i] {
		case 'a', 'e', 'i', 'o', 'u':
			count++
		}
	}
	return count
}
```

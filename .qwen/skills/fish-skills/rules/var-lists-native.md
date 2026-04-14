# All Variables Are Lists

**Rule ID**: `var-lists-native`
**Priority**: CRITICAL
**Category**: Variables & Scoping

## What

All variables in fish are lists, even "scalars" — they are simply lists with one element. Use list operations like indexing, slicing, and `count` to work with variable values.

## Why

Fish's unified list model eliminates the distinction between scalar and array variables found in other shells. This means every variable supports the same operations: indexing, slicing, concatenation, and counting. Understanding this model is essential for correct variable manipulation.

## Examples

### ✅ Correct
```fish
# A "scalar" is just a list with one element
set name "Gazadev"
echo $name           # Full list: Gazadev
echo $name[1]        # First element: Gazadev

# Lists with multiple values
set fruits apple banana cherry
echo $fruits[1]      # apple
echo $fruits[2]      # banana
echo $fruits[-1]     # cherry (negative = from end)
echo $fruits[2..3]   # banana cherry (slicing)

# Count elements
set colors red green blue
count $colors        # 3

# Check if list is empty
set -e empty_var
if test (count $empty_var) -eq 0
    echo "List is empty"
end
```

### ❌ Incorrect
```fish
# Treating variables as scalars when list ops are needed
set files a.txt b.txt c.txt
echo $files          # Works, but prints all on separate lines

# Bash-style ${#var} for length doesn't exist
set text "hello"
echo ${#text}        # ERROR: no such syntax in fish

# Accessing index 0 (fish is 1-indexed)
set items x y z
echo $items[0]       # ERROR: fish lists are 1-indexed
```

## Best Practices

```fish
# Safe access with existence check
set -q myvar[1]
and echo "First element exists"
or echo "List is empty or unset"

# Slicing with ranges
set nums one two three four five
echo $nums[1..3]     # one two three
echo $nums[3..]      # three four five (from index 3 to end)
echo $nums[..2]      # one two (from start to index 2)

# Appending to lists
set colors red green
set colors $colors blue    # Append
set colors purple $colors  # Prepend

# List concatenation
set a 1 2 3
set b 4 5 6
set combined $a $b    # 1 2 3 4 5 6

# Iterating safely
set -e dirs
for d in $dirs        # Loop body never executes if empty
    echo $d
end
```

## See Also

- [`var-set-syntax`](var-set-syntax.md) - Use `set` to define variables
- [`var-argv-not-numbered`](var-argv-not-numbered.md) - $argv is also a list
- [`cmdsub-newline-split`](cmdsub-newline-split.md) - Command output splits into list elements

# 🔍 Task Filtering Guide

Complete guide to filtering tasks in PawPal+ by completion status, pet name, category, and more.

---

## 📚 Available Filtering Methods

### 1. **Owner.filter_tasks()** - Flexible Multi-Criteria Filtering

The most powerful filtering method - combine multiple criteria in one call.

**Location:** [pawpal_system.py:177-226](pawpal_system.py#L177-L226)

**Signature:**
```python
def filter_tasks(
    self,
    pet_name: Optional[str] = None,
    completed: Optional[bool] = None,
    category: Optional[TaskCategory] = None,
    overdue_only: bool = False
) -> List[Task]
```

**Parameters:**
- `pet_name` - Filter by specific pet (e.g., "Buddy", "Whiskers")
- `completed` - Filter by status (True = completed, False = pending, None = all)
- `category` - Filter by task category (e.g., TaskCategory.FEEDING)
- `overdue_only` - If True, only return overdue pending tasks

---

### 2. **Pet.filter_tasks()** - Pet-Level Filtering

Filter tasks for a specific pet.

**Location:** [pawpal_system.py:119-158](pawpal_system.py#L119-L158)

**Signature:**
```python
def filter_tasks(
    self,
    completed: Optional[bool] = None,
    category: Optional[TaskCategory] = None,
    overdue_only: bool = False
) -> List[Task]
```

---

### 3. **Legacy Methods** (Still Available)

Simple single-criterion filters:

- `owner.get_tasks_by_pet(pet_name)` - Get all tasks for one pet
- `owner.get_tasks_by_status(completed)` - Get tasks by completion status
- `owner.get_tasks_by_category(category)` - Get tasks by category
- `owner.get_overdue_tasks()` - Get all overdue tasks
- `owner.get_recurring_tasks()` - Get all recurring tasks

---

## 🎯 Usage Examples

### Example 1: Filter by Completion Status

```python
owner = Owner("Jordan", available_time=480)

# Get all completed tasks
completed = owner.filter_tasks(completed=True)

# Get all pending (incomplete) tasks
pending = owner.filter_tasks(completed=False)

# Get all tasks regardless of status
all_tasks = owner.filter_tasks()
```

**Output:**
```
✅ Completed: ['Feed Buddy', 'Walk Whiskers']
⏳ Pending: ['Groom Buddy', 'Play fetch', 'Clean cage']
```

---

### Example 2: Filter by Pet Name

```python
# Get all tasks for Buddy (both pending and completed)
buddy_tasks = owner.filter_tasks(pet_name="Buddy")

# Get only Buddy's pending tasks
buddy_pending = owner.filter_tasks(pet_name="Buddy", completed=False)

# Get only Buddy's completed tasks
buddy_done = owner.filter_tasks(pet_name="Buddy", completed=True)
```

**Output:**
```
🐕 Buddy's tasks: 4 total
  ⏳ Morning walk
  ✅ Feed Buddy
  ⏳ Play fetch
  ⏳ Groom Buddy
```

---

### Example 3: Filter by Category

```python
# Get all feeding tasks
feeding = owner.filter_tasks(category=TaskCategory.FEEDING)

# Get pending grooming tasks
grooming_pending = owner.filter_tasks(
    category=TaskCategory.GROOMING,
    completed=False
)

# Get completed medication tasks
meds_done = owner.filter_tasks(
    category=TaskCategory.MEDICATION,
    completed=True
)
```

**Output:**
```
🍽️ Feeding tasks: 3 total
  ✅ Feed Buddy
  ⏳ Feed Whiskers
  ⏳ Feed Tweety
```

---

### Example 4: Filter by Multiple Criteria

Combine filters to get very specific results:

```python
# Buddy's pending feeding tasks
buddy_feeding = owner.filter_tasks(
    pet_name="Buddy",
    completed=False,
    category=TaskCategory.FEEDING
)

# Whiskers' completed grooming tasks
whiskers_grooming = owner.filter_tasks(
    pet_name="Whiskers",
    completed=True,
    category=TaskCategory.GROOMING
)

# All completed walking tasks across all pets
walks_done = owner.filter_tasks(
    completed=True,
    category=TaskCategory.WALKING
)
```

---

### Example 5: Filter Overdue Tasks

```python
# Get all overdue tasks
all_overdue = owner.filter_tasks(overdue_only=True)

# Get Buddy's overdue tasks
buddy_overdue = owner.filter_tasks(
    pet_name="Buddy",
    overdue_only=True
)

# Get overdue feeding tasks
overdue_feeding = owner.filter_tasks(
    category=TaskCategory.FEEDING,
    overdue_only=True
)
```

**Output:**
```
⚠️ Overdue tasks: 2 total
  🔴 Play fetch (Buddy) - 1.5 hours overdue
  🔴 Clean litter box (Whiskers) - 2.3 hours overdue
```

---

### Example 6: Pet-Level Filtering

Filter tasks directly on a Pet object:

```python
buddy = owner.pets[0]  # Get Buddy

# Get Buddy's pending tasks
pending = buddy.filter_tasks(completed=False)

# Get Buddy's feeding tasks
feeding = buddy.filter_tasks(category=TaskCategory.FEEDING)

# Get Buddy's overdue tasks
overdue = buddy.filter_tasks(overdue_only=True)

# Get Buddy's pending grooming tasks
grooming = buddy.filter_tasks(
    completed=False,
    category=TaskCategory.GROOMING
)
```

---

## 🎨 Practical Use Cases

### Use Case 1: Daily Task Dashboard

Show what needs to be done today for each pet:

```python
for pet in owner.pets:
    pending = owner.filter_tasks(pet_name=pet.name, completed=False)
    overdue = owner.filter_tasks(pet_name=pet.name, overdue_only=True)

    print(f"\n{pet.name}:")
    print(f"  Pending: {len(pending)} tasks")
    print(f"  Overdue: {len(overdue)} tasks ⚠️")

    for task in pending:
        status = "⚠️ OVERDUE" if task.is_overdue() else ""
        print(f"    - {task.description} {status}")
```

**Output:**
```
Buddy:
  Pending: 3 tasks
  Overdue: 1 tasks ⚠️
    - Morning walk
    - Play fetch ⚠️ OVERDUE
    - Groom Buddy

Whiskers:
  Pending: 2 tasks
  Overdue: 1 tasks ⚠️
    - Clean litter box ⚠️ OVERDUE
    - Brush cat
```

---

### Use Case 2: Category Progress Report

Track completion by category:

```python
for category in TaskCategory:
    total = owner.filter_tasks(category=category)
    completed = owner.filter_tasks(category=category, completed=True)
    pending = owner.filter_tasks(category=category, completed=False)

    if total:
        completion_rate = (len(completed) / len(total)) * 100
        print(f"{category.value.title()}: {completion_rate:.0f}% complete")
        print(f"  ✅ {len(completed)} done, ⏳ {len(pending)} pending")
```

**Output:**
```
Feeding: 67% complete
  ✅ 2 done, ⏳ 1 pending
Walking: 50% complete
  ✅ 1 done, ⏳ 1 pending
Grooming: 0% complete
  ✅ 0 done, ⏳ 2 pending
```

---

### Use Case 3: Urgent Tasks Alert

Find all tasks that need immediate attention:

```python
urgent_tasks = owner.filter_tasks(overdue_only=True)

if urgent_tasks:
    print(f"⚠️ ALERT: {len(urgent_tasks)} overdue tasks!")
    for task in urgent_tasks:
        hours_overdue = (datetime.now() - task.due_time).total_seconds() / 3600
        print(f"  🔴 {task.description} ({task.pet_name})")
        print(f"     Overdue by {hours_overdue:.1f} hours")
else:
    print("✅ No overdue tasks - you're all caught up!")
```

---

### Use Case 4: Pet-Specific Care Checklist

Generate a care checklist for a specific pet:

```python
def generate_care_checklist(owner, pet_name):
    """Generate a comprehensive care checklist for a pet"""
    print(f"\n📋 Care Checklist for {pet_name}\n")

    # Group by category
    for category in TaskCategory:
        tasks = owner.filter_tasks(
            pet_name=pet_name,
            category=category,
            completed=False
        )

        if tasks:
            print(f"  {category.value.title()}:")
            for task in tasks:
                overdue = " ⚠️" if task.is_overdue() else ""
                print(f"    [ ] {task.description}{overdue}")

# Use it
generate_care_checklist(owner, "Buddy")
```

**Output:**
```
📋 Care Checklist for Buddy

  Walking:
    [ ] Morning walk
  Feeding:
    [ ] Feed Buddy
  Playtime:
    [ ] Play fetch ⚠️
  Grooming:
    [ ] Groom Buddy
```

---

## 💡 Comparison: Old vs New

### Old Way (Multiple Calls)

```python
# To get Buddy's pending tasks, you needed:
all_buddy_tasks = owner.get_tasks_by_pet("Buddy")
buddy_pending = [t for t in all_buddy_tasks if not t.is_completed]

# To get completed feeding tasks:
all_feeding = owner.get_tasks_by_category(TaskCategory.FEEDING)
completed_feeding = [t for t in all_feeding if t.is_completed]
```

### New Way (Single Call)

```python
# Get Buddy's pending tasks in one call
buddy_pending = owner.filter_tasks(pet_name="Buddy", completed=False)

# Get completed feeding tasks in one call
completed_feeding = owner.filter_tasks(
    completed=True,
    category=TaskCategory.FEEDING
)
```

**Benefits:**
- ✅ Cleaner, more readable code
- ✅ Fewer lines of code
- ✅ More flexible - combine any criteria
- ✅ Better performance (single pass through tasks)

---

## 🔧 Advanced Filtering Patterns

### Pattern 1: Chain Filters with Sorting

```python
# Get Buddy's pending tasks sorted by priority
tasks = owner.filter_tasks(pet_name="Buddy", completed=False)
sorted_tasks = owner.sort_tasks_by_priority(tasks, ascending=True)
```

### Pattern 2: Filter and Count

```python
# Count overdue tasks per pet
for pet in owner.pets:
    count = len(owner.filter_tasks(pet_name=pet.name, overdue_only=True))
    if count > 0:
        print(f"⚠️ {pet.name} has {count} overdue tasks!")
```

### Pattern 3: Nested Filtering

```python
# Get high-priority pending tasks per category
from collections import defaultdict

urgent_by_category = defaultdict(list)

for category in TaskCategory:
    tasks = owner.filter_tasks(category=category, completed=False)
    high_priority = [t for t in tasks if t.priority == 1]
    if high_priority:
        urgent_by_category[category] = high_priority

# Display
for category, tasks in urgent_by_category.items():
    print(f"{category.value.title()}: {len(tasks)} urgent tasks")
```

---

## 📊 Quick Reference Table

| What You Want | Method Call |
|--------------|-------------|
| All completed tasks | `owner.filter_tasks(completed=True)` |
| All pending tasks | `owner.filter_tasks(completed=False)` |
| All tasks for "Buddy" | `owner.filter_tasks(pet_name="Buddy")` |
| Buddy's pending tasks | `owner.filter_tasks(pet_name="Buddy", completed=False)` |
| All feeding tasks | `owner.filter_tasks(category=TaskCategory.FEEDING)` |
| Pending feeding tasks | `owner.filter_tasks(category=TaskCategory.FEEDING, completed=False)` |
| All overdue tasks | `owner.filter_tasks(overdue_only=True)` |
| Buddy's overdue tasks | `owner.filter_tasks(pet_name="Buddy", overdue_only=True)` |
| Buddy's pending feeding | `owner.filter_tasks(pet_name="Buddy", completed=False, category=TaskCategory.FEEDING)` |
| Pet-level filtering | `pet.filter_tasks(completed=False)` |

---

## ⚙️ Implementation Details

### Algorithm Complexity
- **Time:** O(n) where n = number of tasks
- **Space:** O(k) where k = number of matching tasks

### Filtering Process
1. Start with all tasks (Owner) or pet's tasks (Pet)
2. Apply each filter sequentially:
   - Pet name filter (Owner only)
   - Completion status filter
   - Category filter
   - Overdue filter
3. Return filtered list

### Notes
- All filters use list comprehensions for efficiency
- Filters are applied in order for optimal performance
- `None` values mean "no filter" for that criterion
- `overdue_only` only applies to pending tasks (ignores completed)

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_filtering.py
```

Tests cover:
- ✅ Filtering by completion status
- ✅ Filtering by pet name
- ✅ Filtering by category
- ✅ Multi-criteria filtering
- ✅ Overdue task filtering
- ✅ Pet-level filtering
- ✅ Practical use cases

---

**Created:** February 15, 2026
**Version:** 2.0
**Related:** [NEW_FEATURES.md](NEW_FEATURES.md)

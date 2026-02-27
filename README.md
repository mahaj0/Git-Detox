'''# Git Detox 🎨

**Git Detox** is your Git safety net. It's a tool that visualizes local Git activity (branches, stashes, reflog, dangling commits) in a unified view and highlights recoverable or at-risk work.

## Features

- **Scan for Recoverable Work**: Detects deleted branches, dangling commits, and dropped stashes.
- **Risk Detection**: Highlights work at risk of being lost to Git's garbage collection.
- **Hygiene Analysis**: Identifies merged and stale branches to keep your repo clean.
- **Visual TUI**: Interactive terminal interface for exploring and restoring your Git history.
- **Safe Recovery**: Preview commands before execution with guided restoration.

## Installation

```bash
# Clone the repository
git clone https://github.com/youruser/git-detox.git
cd git-detox

# Install in editable mode
pip install -e .
```

## Usage

### CLI Commands

- `git-detox scan`: List all recoverable items in the current repository.
- `git-detox show <ID>`: View detailed information and diff summary for an item.
- `git-detox restore <ID>`: Safely restore an item to a new branch.
- `git-detox health`: Get a hygiene report and health score for your repo.
- `git-detox tui`: Launch the interactive terminal UI.

### Example

```bash
$ git-detox scan
Scanning repository...
                              Recoverable Git Work                              
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ ID          ┃ Type           ┃ Source/Ref ┃ Subject         ┃ Risk   ┃ Date           ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ del_abc1234 │ deleted_branch │ feature-x  │ Fix login bug   │ low    │ 2026-02-13     │
└─────────────┴────────────────┴────────────┴─────────────────┴────────┴────────────────┘
```

## Strategic Advice for Users

1. **Don't Panic**: If you just deleted a branch or reset your HEAD, `git-detox` can likely find it in the reflog.
2. **Check Health Regularly**: Use `git-detox health` to keep your local environment lean.
3. **Preview Before Restore**: Always use `show` to verify the content before restoring.

## License

MIT
'''

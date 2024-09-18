<table style="border: none;">
<tr style="border: none;">
  <td style="border: none;">
    <img src="./icon.svg">
  </td>
  <td style="border: none;">
    <h1>NotionTodoistSyncer</h1>
  </td>
</tr>
</table>

A self-hosted bidirectional Syncer for Notion and Todoist because screw paying for Zapier, IFTTT, and 2Sync.

## Setup
### config.json
```json
{
    "todoist_api_key": "",
    "notion_api_key": "",
    "database_id": "",
    "project_id": "",
    "notion_status_tag_name": "Status",
    "notion_done_status": "Completed",
    "notion_default_status": "Next Up"
}
```
## Todo

- [x] Todoist-To-Notion
  - [x]   Deleted Notes
  - [x]   Completed Notes
  - [x]   New notes
    - [x] Title
    - [x] Content
    - [x] Due date
    - [x] Priority        
- [ ] Notion-To-Todoist
  - [ ]   Deleted Notes
  - [ ]   Completed Notes
  - [ ]   New notes
    - [ ] Title
    - [ ] Content
    - [ ] Due date
    - [ ] Priority
- [ ] Refactor and Clean up code
- [ ] Improve performance
- [ ] GUI?
- [ ] Sync Reports (i.e failure/success/total/new)
- [ ] Switch to SQLite over TinyDB for note sync cache

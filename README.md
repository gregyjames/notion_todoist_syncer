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

A self-hosted bidirectional sync tool for Notion and Todoist to eliminate the need for paid services like Zapier, IFTTT, and 2Sync. This solution was designed for personal use, combining my preference for Notion's powerful database capabilities with Todoist's ease of use for task management. By simplifying the process, I no longer need to navigate Notion's interface just to add a new task, streamlining my workflow effectively.

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
  - [ ]   Deleted Notes
  - [x]   Completed Notes
  - [x]   New notes
    - [x] Title
    - [x] Content
    - [ ] Due date
    - [x] Priority
  - [ ] Note property changes        
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
- [ ] Package into container

## License 
MIT License

Copyright (c) 2024 Greg James

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

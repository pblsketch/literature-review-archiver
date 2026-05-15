# Implementation Plan - Notero Integration & Metadata Correction

## User Review Required
> [!IMPORTANT]
> **Notion Property Name Changes**: The code will now expect the Notion database to have **English** property names as shown in your screenshot.
> - `논문 제목` -> `Name`
> - `저자` -> `Authors`
> - `발행연도` -> `Date` (Number type)
> - `학술지명/출처` -> `Publication`
> - `페이지` -> `Pages`
> - `핵심 키워드` -> `Tags` (or `Keywords`?) *Screenshot says `Tags`*
> - `권(호)` -> `Volume` / `Issue`
> - `URL/DOI` -> `DOI` / `URL`
> - `읽음 상태` -> `Status` (Assuming English key)

## Proposed Changes

### Logic Change: `Create` -> `Search & Update`
Currently, the tool blindly creates a new page. The new logic will be:
1.  **Search**: Try to find an existing page in Notion using the **Title** (or DOI if available).
2.  **Match Found**:
    -   **Validation**: Compare Gemini's extracted metadata (Year, Authors) with the existing Notion data.
    -   **Correction**: If Gemini provides data where Notion is empty or looks wrong (optional), update the property.
    -   **Append**: Add the AI Analysis (Summary) to the page body.
    -   **Upload**: Add the Google Drive link if missing.
3.  **No Match**: Fallback to creating a new page (as before).

### `utils/notion_utils.py`
#### [MODIFY] `create_notion_page` -> `update_or_create_notion_page`
-   Implement `search_notion_page(client, database_id, title)`
-   Update the property mapping dictionary to use English keys:
    ```python
    props_map = {
        "Name": title,
        "Authors": authors,
        "Date": year,  # Number
        "Publication": journal,
        "DOI": doi,
        "Status": "To Read"
        # ...
    }
    ```

### `app.py`
#### [MODIFY] Main Workflow
-   Call the new `update_or_create_notion_page` function.
-   Log whether a page was **Created** (New) or **Updated** (Existing).

## Verification Plan
1.  **Manual Test**: Run the tool with a PDF that *already exists* in Notion (synced by Notero).
2.  **Expectation**: The tool should say "Found existing page..." and add the summary to it, instead of creating a duplicate.

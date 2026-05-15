# Task: Notero Integration & Metadata Validation

## Status
- [ ] **Implementation Plan**: Create detailed plan for Notero-compatible logic <!-- id: 0 -->
- [ ] **Property Mapping**: Update `notion_utils.py` to use English column names (`Name`, `Authors`, `Date`...) <!-- id: 1 -->
- [ ] **Search Logic**: Implement `find_page_by_properties` in `notion_utils.py` (Search by Title or DOI) <!-- id: 2 -->
- [ ] **Update Logic**: Implement `update_page_metadata` to compare and fix Zotero data with Gemini data <!-- id: 3 -->
- [ ] **Integration**: Modify `app.py` to use the new `update_or_create` workflow <!-- id: 4 -->
- [ ] **Verification**: Test with recent paper <!-- id: 5 -->

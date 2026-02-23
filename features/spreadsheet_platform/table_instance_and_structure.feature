Feature: Spreadsheet table instance and structure management
    Manage spreadsheet instances, table structure, data, and view configurations.

    Background:
        Given a project "P1" exists
        And a spreadsheet table "T1" exists in project "P1"

    Rule: Table structure supports create, update, delete, and reorder for columns
        Scenario: Maintain columns with order adjustment
            Given table "T1" has columns "需求", "设计", "测试"
            When an actor adds column "预计开始"
            And the actor moves column "预计开始" before column "测试"
            And the actor renames column "设计" to "设计资产"
            Then table "T1" columns become "需求", "设计资产", "预计开始", "测试"

    Rule: Structure operations support batch execution
        Scenario: Apply multiple column changes in one batch request
            Given table "T1" has columns "A", "B", "C"
            When an actor submits a structure batch with operations:
                | op      | column | target   |
                | add     | D      |          |
                | rename  | B      | B_new    |
                | reorder | D      | before C |
            Then all structure operations are applied atomically
            And table "T1" columns become "A", "B_new", "D", "C"

    Rule: Table data supports row and cell mutations including batch writes
        Scenario: Update rows and cells in batch
            Given table "T1" has a row "R1"
            When an actor writes cells in batch:
                | row | column | value    |
                | R1  | 需求   | 登录失败 |
                | R1  | 测试   | 待补充   |
            Then row "R1" stores the written values
            And the write result returns per-cell status

    Rule: A table supports multiple views with configurable filters, sorting, and hidden columns
        Scenario: Configure a kanban view for the same table
            Given table "T1" has an existing grid view "V-grid"
            When an actor creates view "V-kanban" of type "kanban"
            And the actor configures filter "状态 = 待确认"
            And the actor configures sort "预计结束 asc"
            And the actor hides column "设计资产"
            Then table "T1" has views "V-grid" and "V-kanban"
            And view "V-kanban" stores its own filter, sort, and hidden-column settings

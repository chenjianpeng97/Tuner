Feature: Requirement asset management template
    Manage requirement-related files, labels, relationships, and counting semantics.

    Background:
        Given a project "P1" has instantiated requirement templates

    Rule: Product requirement assets support predefined initial file types
        Scenario: Create first-batch asset files for a product requirement
            Given product requirement "PR-1" exists in project "P1"
            When an actor creates asset file "spec.feature" for "PR-1"
            And the actor creates asset file "设计说明.md" for "PR-1"
            And the actor creates asset file "测试用例.md" for "PR-1"
            Then all created files are bound to product requirement "PR-1"

    Rule: Requirement assets support view, edit, and delete
        Scenario: Maintain an existing requirement asset file
            Given product requirement "PR-1" has asset file "设计说明.md"
            When an actor updates file content of "设计说明.md"
            Then the updated content is persisted
            When the actor deletes file "设计说明.md"
            Then file "设计说明.md" is no longer available for "PR-1"

    Rule: Asset labels are project-level configurable and support multiple labels per asset
        Scenario: Assign multiple labels to one asset
            Given project "P1" defines labels "DDL", "自动化测试", "冒烟设计"
            And asset "A1" exists in project "P1"
            When an actor assigns labels "DDL" and "自动化测试" to asset "A1"
            Then asset "A1" is retrievable by each assigned label

    Rule: Pre-uploaded assets can exist before requirement association
        Scenario: Upload asset before creating requirement linkage
            When an actor uploads asset "接口草案.md" into project "P1"
            Then the asset is created with project_id "P1"
            And the asset has no customer requirement or product requirement association yet
            When the actor later links asset "接口草案.md" to product requirement "PR-2"
            Then the association is created successfully

    Rule: Asset copy/follow relations support synchronization choice and branch independence
        Scenario: Follow copy chooses synchronization and then detaches
            Given parent asset "A-parent" exists
            When an actor copies "A-parent" to "A-copy" with follow enabled
            And the actor sets "A-copy" synchronization preference to "manual"
            And parent asset "A-parent" content changes
            Then "A-copy" receives a pending synchronization decision
            When the actor detaches "A-copy" from follow
            Then "A-copy" becomes an independent branch asset

    Rule: Asset counting by customer requirement follows de-duplication and branch rules
        Scenario: Count follow copies once and detached branches independently
            Given customer requirement "CR-1" is associated with product requirements and assets
            And asset "A-parent" and follow copy "A-follow" are both within "CR-1" scope
            And detached branch asset "A-branch" is within "CR-1" scope
            When an actor queries asset statistics for customer requirement "CR-1"
            Then "A-parent" and "A-follow" are counted as one
            And "A-branch" is counted independently

    Rule: Statistics include assets not associated with any requirement
        Scenario: Query independent count for unassociated assets
            Given project "P1" has uploaded assets with no requirement association
            When an actor queries requirement-asset statistics dashboard
            Then the response includes independent count for unassociated assets

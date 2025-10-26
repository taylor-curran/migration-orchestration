"""
COBOL to Spring Boot Migration Task Discovery
Phase 1: Exhaustive task enumeration

Source: og-cics-cobol-app (29 COBOL programs)
Target: target-springboot-cics (Spring Boot + SQLite)

Status Summary:
- 5 programs already migrated (status="completed")
- 9 BMS/UI programs (completed upstream dependencies - REST APIs replace them)
- 15 programs remaining to migrate (status="not-complete")
- 19 total tasks (3 setup + 5 completed migrations + 8 pending migrations + 3 integration)
"""

migration_plan = {
    "tasks": [
        {
            "id": "setup_001",
            "title": "Create Performance Baselines",
            "content": "Measure current COBOL program performance for all business logic programs. Document P50/P95/P99 latencies for CRUD operations and transactions. Establish success metrics for post-migration validation.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "setup_002",
            "title": "Setup Local Monitoring",
            "content": "Configure local observability for Spring Boot application. Add logging, metrics collection, and health checks. Ensure all services emit structured logs for debugging.",
            "status": "not-complete",
            "estimated_hours": 6
        },
        {
            "id": "setup_003",
            "title": "Verify Test Data Generation",
            "content": "Validate BankDataGenerator produces realistic data matching COBOL patterns. Verify 100 customers with 1-5 accounts each. Confirm transaction history generation works correctly.",
            "status": "not-complete",
            "estimated_hours": 6
        },
        
        {
            "id": "migrate_001",
            "title": "Migrate Company Info Program",
            "content": "Port GETCOMPY to CompanyInfoService. Returns fixed company name 'CICS Bank Sample Application'. Simple utility service with no database access.",
            "status": "completed",
            "estimated_hours": 2
        },
        {
            "id": "migrate_002",
            "title": "Migrate Sort Code Program",
            "content": "Port GETSCODE to SortCodeService. Returns fixed bank sort code '987654'. Simple utility service with no database access.",
            "status": "completed",
            "estimated_hours": 2
        },
        {
            "id": "migrate_003",
            "title": "Migrate Credit Agency Service",
            "content": "Port CRDTAGY1 to CreditAgencyService. Implements random delay simulation, credit score generation, and customer record updates. Includes async processing patterns.",
            "status": "completed",
            "estimated_hours": 8
        },
        {
            "id": "migrate_004",
            "title": "Migrate Test Data Generator",
            "content": "Port BANKDATA batch program to BankDataGenerator. Generates customers, accounts, and transactions with realistic data. Implements COBOL random seeding and data patterns.",
            "status": "completed",
            "estimated_hours": 12
        },
        {
            "id": "migrate_005",
            "title": "Migrate Error Logging Service",
            "content": "Port ABNDPROC to ErrorLoggingService. Centralizes application error logging to database. Handles error recording with timestamps and diagnostic information.",
            "status": "completed",
            "estimated_hours": 6
        },
        
        {
            "id": "migrate_006",
            "title": "Migrate Credit Agency Dummies",
            "content": "Port CRDTAGY2-5 programs to extend CreditAgencyService. All four programs are identical except container names (CIPB/CIPC/CIPD/CIPE). Implement multi-agency credit scoring with simulated delays.",
            "status": "not-complete",
            "estimated_hours": 6
        },
        {
            "id": "migrate_007",
            "title": "Migrate Customer Create and Update",
            "content": "Port CRECUST and UPDCUST to CustomerService. Implement create with validation, named counter management, and VSAM write. Add update operations with optimistic locking and field-level validation.",
            "status": "not-complete",
            "estimated_hours": 10
        },
        {
            "id": "migrate_008",
            "title": "Migrate Customer Delete and Inquire",
            "content": "Port DELCUS and INQCUST to CustomerService. Implement soft delete with referential integrity checks. Add inquiry operations with efficient lookup by sort code and customer number.",
            "status": "not-complete",
            "estimated_hours": 10
        },
        {
            "id": "migrate_009",
            "title": "Migrate Account Create and Update",
            "content": "Port CREACC and UPDACC to AccountService. Implement create with DB2 transaction handling and PROCTRAN logging. Add update with balance calculations and interest rate adjustments.",
            "status": "not-complete",
            "estimated_hours": 10
        },
        {
            "id": "migrate_010",
            "title": "Migrate Account Delete and Inquire",
            "content": "Port DELACC and INQACC to AccountService. Implement delete with balance validation and audit trail. Add inquiry with account details, transaction history, and balance calculations.",
            "status": "not-complete",
            "estimated_hours": 10
        },
        {
            "id": "migrate_011",
            "title": "Migrate Account Inquiry by Customer",
            "content": "Port INQACCCU to AccountService. Implement customer-based account lookup returning all accounts for a customer. Include sorting, filtering, and pagination for multiple accounts.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "migrate_012",
            "title": "Migrate Debit Credit Function",
            "content": "Port DBCRFUN to TransactionService. Implement debit/credit operations with balance validation, overdraft checks, and transaction logging. Preserve COBOL transaction boundaries with @Transactional.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "migrate_013",
            "title": "Migrate Transfer Function",
            "content": "Port XFRFUN to TransactionService. Implement account-to-account transfers with two-phase commit pattern. Include balance checks, transaction rollback, and audit logging for both accounts.",
            "status": "not-complete",
            "estimated_hours": 12
        },
        
        {
            "id": "integrate_001",
            "title": "Customer Lifecycle Workflow Validation",
            "content": "Test end-to-end customer operations (create, update, inquire, delete). Validate data consistency across operations. Verify credit scoring integration works correctly.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "integrate_002",
            "title": "Account Lifecycle Workflow Validation",
            "content": "Test end-to-end account operations (create, update, inquire, delete). Validate account-customer relationships maintained. Verify balance calculations across operations.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "integrate_003",
            "title": "Transaction Flow Validation",
            "content": "Test debit, credit, and transfer operations in realistic scenarios. Validate transaction logging and balance updates. Verify rollback behavior on failures.",
            "status": "not-complete",
            "estimated_hours": 8
        }
    ]
}

MIGRATED_PROGRAMS = [
    "GETCOMPY.cbl",   # → CompanyInfoService (43 lines)
    "GETSCODE.cbl",   # → SortCodeService (46 lines)
    "CRDTAGY1.cbl",   # → CreditAgencyService (273 lines)
    "BANKDATA.cbl",   # → BankDataGenerator (1463 lines)
    "ABNDPROC.cbl"    # → ErrorLoggingService (176 lines)
]

BMS_UI_PROGRAMS = [
    "BNK1CAC.cbl",    # Create Account screen (1298 lines) - REST API replaces
    "BNK1CCA.cbl",    # Create Customer screen (952 lines) - REST API replaces
    "BNK1CCS.cbl",    # Customer Search screen (1657 lines) - REST API replaces
    "BNK1CRA.cbl",    # Account Read screen (1166 lines) - REST API replaces
    "BNK1DAC.cbl",    # Delete Account screen (1158 lines) - REST API replaces
    "BNK1DCS.cbl",    # Delete Customer screen (2053 lines) - REST API replaces
    "BNK1TFN.cbl",    # Transfer Function screen (1224 lines) - REST API replaces
    "BNK1UAC.cbl",    # Update Account screen (1405 lines) - REST API replaces
    "BNKMENU.cbl"     # Main menu screen (1311 lines) - REST API replaces
]

REMAINING_TO_MIGRATE = [
    "CRDTAGY2.cbl",   # Credit agency dummy (273 lines)
    "CRDTAGY3.cbl",   # Credit agency dummy (272 lines)
    "CRDTAGY4.cbl",   # Credit agency dummy (275 lines)
    "CRDTAGY5.cbl",   # Credit agency dummy (275 lines)
    "CRECUST.cbl",    # Create customer (1439 lines)
    "UPDCUST.cbl",    # Update customer (364 lines)
    "DELCUS.cbl",     # Delete customer (761 lines)
    "INQCUST.cbl",    # Inquire customer (711 lines)
    "CREACC.cbl",     # Create account (1247 lines)
    "UPDACC.cbl",     # Update account (406 lines)
    "DELACC.cbl",     # Delete account (649 lines)
    "INQACC.cbl",     # Inquire account (1002 lines)
    "INQACCCU.cbl",   # Inquire account by customer (882 lines)
    "DBCRFUN.cbl",    # Debit/credit function (861 lines)
    "XFRFUN.cbl"      # Transfer function (1924 lines)
]
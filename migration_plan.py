
migration_plan = {
    "tasks": [
        {
            "id": "setup_001",
            "title": "Create Performance Baselines",
            "content": "Measure current COBOL program performance for key operations. Document P50/P95/P99 latencies for customer, account, and transaction operations. Establish success criteria for migration validation.",
            "status": "not-complete",
            "depends_on": [],
            "deliverables": [
                "performance_baseline.json",
                "performance_dashboard.html"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "Performance metrics exported to performance_baseline.json containing P50/P95/P99 latencies for all 11 business logic programs. Each program measured under load with 100+ samples. Baseline dashboard displays metrics with timestamps.",
            "action": "Measure P50/P95/P99 latencies for all 11 COBOL business logic programs under load and create baseline dashboard. No performance_baseline.json or performance_dashboard.html files exist yet."
        },
        {
            "id": "setup_002",
            "title": "Setup Local SQLite Database",
            "content": "Create SQLite schema matching COBOL data structures. Load test data fixtures for customers, accounts, and transactions. Configure Spring datasource for local development.",
            "status": "not-complete",
            "depends_on": [],
            "deliverables": [
                "banking.db",
                "schema.sql",
                "test_data_fixtures.sql"
            ],
            "estimated_hours": 6,
            "validation_mechanism": "SQLite database file exists with all 4 tables (Customer, Account, Transaction, PROCTRAN) containing test fixtures. Schema validation query confirms all constraints, indexes, and foreign keys. Spring Boot application starts successfully with datasource connected.",
            "action": "Create banking.db database file and test_data_fixtures.sql. Schema.sql exists with all 4 tables defined but database file and test fixtures missing. Initialize database and verify Spring Boot datasource connects."
        },
        {
            "id": "setup_003",
            "title": "Configure Local Monitoring",
            "content": "Set up local logging and metrics collection. Configure Spring Boot Actuator for health checks. Implement basic request/response logging for debugging.",
            "status": "not-complete",
            "depends_on": [],
            "deliverables": [
                "application.yml",
                "logback.xml"
            ],
            "estimated_hours": 6,
            "validation_mechanism": "Spring Boot Actuator /health endpoint returns UP status. /metrics endpoint exposes request timing and JVM metrics. Log files contain structured request/response logging with correlation IDs for all API calls.",
            "action": "Create logback.xml for structured logging with correlation IDs. Application.properties exists but logback.xml missing. Verify Spring Boot Actuator /health and /metrics endpoints are accessible."
        },
        
        {
            "id": "validator_001",
            "title": "Create Database Schema Tests",
            "content": "Build tests to verify all tables created correctly. Check constraints, indexes, and foreign keys. Test database connections and basic CRUD operations on all entities (Customer, Account, Transaction, PROCTRAN).",
            "status": "not-complete",
            "depends_on": ["setup_002"],
            "deliverables": [
                "SchemaValidationTest.java",
                "DatabaseTestConfig.java"
            ],
            "estimated_hours": 6,
            "validation_mechanism": "JUnit test suite with 15+ tests covering all 4 tables achieves 95%+ branch coverage via JaCoCo. All constraint, index, and foreign key validations pass. CRUD operations execute without errors on all entities.",
            "action": "Fix JaCoCo report generation to verify 95%+ branch coverage. DatabaseSchemaConsistencyTest exists and passes but no JaCoCo coverage report was generated. Add remaining tests if needed to cover all 4 tables."
        },
        {
            "id": "validator_002",
            "title": "Create Customer Read Test Suite",
            "content": "Build unit tests for INQCUST customer retrieval operations. Create at least one integration test covering the main success path. Test composite key lookups (sort code + customer number), VSAM record mapping, and error handling for missing customers.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "CustomerControllerTest.java",
                "CustomerServiceTest.java",
                "customer_test_fixtures.json"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on CustomerController and CustomerService. Test suite includes 20+ test cases covering composite key lookups, missing customer scenarios, and DTO mapping. All tests pass in CI pipeline.",
            "action": "Implement CustomerService and CustomerController first, then write CustomerServiceTest.java and CustomerControllerTest.java covering INQCUST operations achieving 90%+ branch coverage. No CustomerService or CustomerController exists yet."
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Read Operations",
            "content": "Port INQCUST to Spring Boot REST endpoint for customer retrieval. Map COBOL records to DTOs and implement repository with composite key support.",
            "status": "not-complete",
            "depends_on": ["validator_002"],
            "deliverables": [
                "CustomerController.java",
                "CustomerService.java",
                "CustomerRepository.java",
                "CustomerDTO.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "validator_002 test suite passes with 90%+ branch coverage via JaCoCo. Integration tests verify REST endpoint returns correct customer data. Response times within 10% of performance baseline for customer lookups.",
            "action": "Implement CustomerController, CustomerService, and CustomerDTO. Port INQCUST logic from COBOL to REST endpoint with composite key support. CustomerRepository interface exists but no service or controller exists yet."
        },
        {
            "id": "validator_003",
            "title": "Create Customer Create Test Suite",
            "content": "Build unit tests for CRECUST customer creation operations. Create at least one integration test for the complete creation flow. Test Named Counter generation, async credit agency integration with mocks, VSAM/DB2 writes, PROCTRAN audit logging, and rollback scenarios.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "CustomerServiceTest.java",
                "NamedCounterServiceTest.java",
                "credit_agency_mocks.json"
            ],
            "estimated_hours": 10,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on CustomerService and NamedCounterService. Test suite includes 25+ test cases covering async credit checks with mocks, counter generation, PROCTRAN logging, and rollback scenarios. All tests pass with proper transaction boundaries verified.",
            "action": "Implement CustomerService and NamedCounterService first, then write CustomerServiceTest.java and NamedCounterServiceTest.java covering CRECUST operations with async credit check mocks achieving 90%+ coverage. No CustomerService exists yet."
        },
        {
            "id": "migrate_002",
            "title": "Migrate Customer Create Operations",
            "content": "Port CRECUST to Spring Boot customer creation endpoint with async credit agency integration. Implement Named Counter with distributed locks for customer numbers. Handle DB2/VSAM writes and PROCTRAN audit logging.",
            "status": "not-complete",
            "depends_on": ["validator_003", "migrate_001"],
            "deliverables": [
                "CustomerService.java",
                "CreditAgencyService.java",
                "NamedCounterService.java"
            ],
            "estimated_hours": 12,
            "validation_mechanism": "validator_003 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Integration tests verify customer creation with unique counter-generated numbers. PROCTRAN audit records created for all operations. Response times within 15% of baseline.",
            "action": "Add POST method to CustomerController and CustomerService. Port CRECUST logic from COBOL. Implement NamedCounterService with distributed locks for customer number generation. CreditAgencyService exists but CustomerService and NamedCounterService do not exist yet."
        },
        {
            "id": "validator_004",
            "title": "Create Customer Update/Delete Test Suite",
            "content": "Build unit tests for UPDCUST and DELCUS operations. Create integration tests for cascade delete (customer → accounts). Test limited field updates in UPDCUST, cascade delete logic in DELCUS with PROCTRAN logging, and error handling.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "CustomerServiceTest.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on CustomerService update/delete methods. Test suite includes 20+ tests covering cascade deletes with account orphan verification, PROCTRAN audit for deletes only, and field update validation. All tests pass verifying no orphaned accounts.",
            "action": "Implement CustomerService with update/delete methods first, then write CustomerServiceTest.java covering UPDCUST and DELCUS operations with cascade delete verification achieving 90%+ coverage. No CustomerService exists yet."
        },
        {
            "id": "migrate_003",
            "title": "Migrate Customer Update Delete",
            "content": "Port UPDCUST and DELCUS to update/delete endpoints. UPDCUST modifies limited fields without PROCTRAN. DELCUS cascades to delete all customer accounts then customer record with PROCTRAN logging.",
            "status": "not-complete",
            "depends_on": ["validator_004", "migrate_001", "migrate_002"],
            "deliverables": [
                "CustomerService.java"
            ],
            "estimated_hours": 10,
            "validation_mechanism": "validator_004 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Database queries confirm zero orphaned accounts after cascade deletes. PROCTRAN records exist only for delete operations, not updates. Response times within 10% of baseline.",
            "action": "Add PUT and DELETE methods to CustomerController and CustomerService. Port UPDCUST and DELCUS logic from COBOL. Implement cascade delete logic for associated accounts. Handle PROCTRAN logging for deletes only. No CustomerController or CustomerService exists yet."
        },
        {
            "id": "validator_005",
            "title": "Create Account Read Test Suite",
            "content": "Build unit tests for INQACC and INQACCCU account query operations. Create integration tests for pagination/cursor patterns. Test single account lookup by number, customer account listing with pagination, and DB2 cursor handling.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "AccountControllerTest.java",
                "AccountServiceTest.java",
                "account_test_fixtures.json"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on AccountController and AccountService. Test suite includes 22+ tests covering single account queries, paginated customer account lists, and cursor handling. All pagination edge cases verified with test data.",
            "action": "Implement AccountService and AccountController first, then write AccountServiceTest.java and AccountControllerTest.java covering INQACC and INQACCCU operations with pagination achieving 90%+ coverage. No AccountService or AccountController exists yet."
        },
        {
            "id": "migrate_004",
            "title": "Migrate Account Read Operations",
            "content": "Port INQACC and INQACCCU to AccountService endpoints. INQACC queries by account number. INQACCCU queries all accounts for customer using cursor/pagination.",
            "status": "not-complete",
            "depends_on": ["validator_005"],
            "deliverables": [
                "AccountController.java",
                "AccountService.java",
                "AccountRepository.java",
                "AccountDTO.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "validator_005 test suite passes with 90%+ branch coverage via JaCoCo. Integration tests verify REST endpoints return correct account data with proper pagination. Response times within 10% of baseline for single and paginated queries.",
            "action": "Implement AccountController, AccountService, and AccountDTO. Port INQACC and INQACCCU logic from COBOL to REST endpoints with cursor pagination support. AccountRepository interface exists but no service or controller exists yet."
        },
        {
            "id": "validator_006",
            "title": "Create Account Create Test Suite",
            "content": "Build unit tests for CREACC account creation operations. Create integration test for the complete creation flow. Test Named Counter generation for account numbers, enqueue/dequeue logic, DB2 writes, PROCTRAN logging, and rollback on failure.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "AccountServiceTest.java",
                "NamedCounterServiceTest.java"
            ],
            "estimated_hours": 9,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on AccountService and NamedCounterService. Test suite includes 23+ tests covering counter generation with enqueue/dequeue, PROCTRAN audit logging, and rollback scenarios. All tests verify proper transaction boundaries and counter consistency.",
            "action": "Implement AccountService and NamedCounterService first, then write AccountServiceTest.java and NamedCounterServiceTest.java covering CREACC operations with Named Counter logic achieving 90%+ coverage. No AccountService or NamedCounterService exists yet."
        },
        {
            "id": "migrate_005",
            "title": "Migrate Account Create Operations",
            "content": "Port CREACC to Spring Boot account creation endpoint. Implement Named Counter with enqueue/dequeue for account numbers. Handle DB2 writes, PROCTRAN logging, and rollback on failure.",
            "status": "not-complete",
            "depends_on": ["validator_006", "migrate_002", "migrate_004"],
            "deliverables": [
                "AccountService.java",
                "NamedCounterService.java"
            ],
            "estimated_hours": 10,
            "validation_mechanism": "validator_006 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Integration tests confirm unique account numbers generated via counter. PROCTRAN audit records created for all account creations. Response times within 15% of baseline.",
            "action": "Add POST method to AccountController and AccountService. Port CREACC logic from COBOL. Implement NamedCounterService with enqueue/dequeue for account number generation. Handle PROCTRAN logging and rollback on failure. No AccountService or NamedCounterService exists yet."
        },
        {
            "id": "validator_007",
            "title": "Create Account Update/Delete Test Suite",
            "content": "Build unit tests for UPDACC and DELACC operations. Create integration tests for update scenarios. Test field modifications (type, interest rate, overdraft, dates), account deletion with PROCTRAN logging, and validation of business rules.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "AccountServiceTest.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on AccountService update/delete methods. Test suite includes 18+ tests covering field updates, business rule validation, and PROCTRAN audit for deletes. All tests pass verifying proper state transitions.",
            "action": "Implement AccountService with update/delete methods first, then write AccountServiceTest.java covering UPDACC and DELACC operations achieving 90%+ coverage. No AccountService exists yet."
        },
        {
            "id": "migrate_006",
            "title": "Migrate Account Update Delete",
            "content": "Port UPDACC and DELACC to update/delete endpoints. UPDACC modifies type, interest rate, overdraft, statement dates. DELACC deletes account with PROCTRAN logging.",
            "status": "not-complete",
            "depends_on": ["validator_007", "migrate_004", "migrate_005"],
            "deliverables": [
                "AccountService.java"
            ],
            "estimated_hours": 9,
            "validation_mechanism": "validator_007 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Integration tests verify field updates persist correctly. PROCTRAN records exist for delete operations. Response times within 10% of baseline for update and delete operations.",
            "action": "Add PUT and DELETE methods to AccountController and AccountService. Port UPDACC and DELACC logic from COBOL. Implement business rule validation and PROCTRAN logging for deletes. No AccountController or AccountService exists yet."
        },
        {
            "id": "validator_008",
            "title": "Create Transfer Funds Test Suite",
            "content": "Build unit tests for XFRFUN transfer operations. Create integration tests for atomic dual-account updates. Test debit/credit balance updates, transaction rollback scenarios, PROCTRAN audit logging, insufficient funds handling, and atomicity guarantees.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "TransactionServiceTest.java",
                "TransferFundsTest.java",
                "transfer_test_fixtures.json"
            ],
            "estimated_hours": 10,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on TransactionService transfer methods. Test suite includes 28+ tests covering atomic dual-account updates, rollback scenarios, insufficient funds, and PROCTRAN logging. All tests verify atomicity with database state checks.",
            "action": "Implement TransactionService and TransactionController first, then write TransactionServiceTest.java and TransferFundsTest.java covering XFRFUN operations with atomic dual-account updates achieving 90%+ coverage. No TransactionService or TransactionController exists yet."
        },
        {
            "id": "migrate_007",
            "title": "Migrate Transfer Funds Operations",
            "content": "Port XFRFUN to Spring Boot transfer funds endpoint. Implement atomic debit/credit operations across both accounts. Handle transaction rollback on failure and PROCTRAN audit logging.",
            "status": "not-complete",
            "depends_on": ["validator_008", "migrate_004", "migrate_005"],
            "deliverables": [
                "TransactionController.java",
                "TransactionService.java",
                "TransferDTO.java"
            ],
            "estimated_hours": 12,
            "validation_mechanism": "validator_008 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Integration tests verify atomic balance updates across both accounts with proper rollback on failure. PROCTRAN audit trail complete for all transfers. Response times within 15% of baseline.",
            "action": "Implement TransactionController, TransactionService, and TransferDTO. Port XFRFUN logic from COBOL to REST endpoint with atomic two-phase account updates, balance validation, overdraft checks, and rollback on failure. Handle PROCTRAN audit logging. TransactionRepository interface exists but no service or controller exists yet."
        },
        {
            "id": "validator_009",
            "title": "Create Debit/Credit Test Suite",
            "content": "Build unit tests for DBCRFUN deposit and withdrawal operations. Create integration tests for cash transactions. Test account balance updates (available and actual), transaction logging to PROCTRAN, proper transaction type codes, and error scenarios.",
            "status": "not-complete",
            "depends_on": ["setup_002", "validator_001"],
            "deliverables": [
                "TransactionServiceTest.java",
                "debit_credit_test_fixtures.json"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "JaCoCo reports 90%+ branch coverage on TransactionService debit/credit methods. Test suite includes 20+ tests covering deposits, withdrawals, balance updates, transaction type codes, and PROCTRAN logging. All tests verify correct available and actual balance calculations.",
            "action": "Implement TransactionService first, then write TransactionServiceTest.java covering DBCRFUN operations for deposits and withdrawals achieving 90%+ coverage. No TransactionService exists yet."
        },
        {
            "id": "migrate_008",
            "title": "Migrate Debit Credit Operations",
            "content": "Port DBCRFUN to TransactionService for cash deposits/withdrawals. Update account balances (available and actual). Log transactions to PROCTRAN with proper transaction types.",
            "status": "not-complete",
            "depends_on": ["validator_009", "migrate_004", "migrate_005"],
            "deliverables": [
                "TransactionService.java",
                "DebitCreditDTO.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "validator_009 test suite achieves 80%+ service coverage and 70%+ branch coverage via JaCoCo. Integration tests verify balance updates for both available and actual balances. PROCTRAN records contain correct transaction type codes. Response times within 10% of baseline.",
            "action": "Add debit and credit methods to TransactionController and TransactionService. Port DBCRFUN logic from COBOL. Implement DebitCreditDTO and PROCTRAN audit trail recording with proper transaction type codes. No TransactionController or TransactionService exists yet."
        },
        
        {
            "id": "integrate_001",
            "title": "Integrate Customer Workflows",
            "content": "Test end-to-end customer lifecycle flows. Validate create, read, update, delete operations. Verify credit agency integration and PROCTRAN logging consistency.",
            "status": "not-complete",
            "depends_on": ["migrate_001", "migrate_002", "migrate_003"],
            "deliverables": [
                "CustomerIntegrationTest.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "End-to-end integration tests pass for complete customer lifecycle (create→read→update→delete). PROCTRAN audit trail verified for create and delete operations only. Credit agency async integration completes within 5 seconds. No data inconsistencies detected across 100+ test runs.",
            "action": "Create CustomerIntegrationTest.java. Implement end-to-end tests for complete customer lifecycle (create→read→update→delete) with PROCTRAN audit trail verification and credit agency integration. Verify performance is within acceptable thresholds. No CustomerIntegrationTest.java exists yet."
        },
        {
            "id": "integrate_002",
            "title": "Integrate Account Workflows",
            "content": "Test end-to-end account lifecycle flows. Validate account creation with counter management. Verify cascade delete when customer deleted and PROCTRAN audit trail.",
            "status": "not-complete",
            "depends_on": ["migrate_004", "migrate_005", "migrate_006"],
            "deliverables": [
                "AccountIntegrationTest.java"
            ],
            "estimated_hours": 8,
            "validation_mechanism": "End-to-end integration tests pass for account lifecycle (create→read→update→delete). Database queries confirm zero orphaned accounts after customer cascade deletes. Named Counter generates unique sequential account numbers across 200+ test accounts. PROCTRAN audit complete for all create/delete operations.",
            "action": "Create AccountIntegrationTest.java. Implement end-to-end tests for complete account lifecycle (create→read→update→delete) with cascade delete verification and Named Counter uniqueness testing. Verify PROCTRAN audit trail and performance thresholds. No AccountIntegrationTest.java exists yet."
        },
        {
            "id": "integrate_003",
            "title": "Integrate Transaction Workflows",
            "content": "Test end-to-end transaction processing flows. Validate transfer funds, debit, and credit operations. Verify balance updates, rollback handling, and PROCTRAN consistency.",
            "status": "not-complete",
            "depends_on": ["migrate_007", "migrate_008"],
            "deliverables": [
                "TransactionIntegrationTest.java"
            ],
            "estimated_hours": 10,
            "validation_mechanism": "End-to-end integration tests pass for all transaction types (transfer, debit, credit). Atomic transfer operations verified with intentional failures showing proper rollback. Balance reconciliation matches PROCTRAN audit records across 500+ transactions. Response times within 10% of baseline under load.",
            "action": "Create TransactionIntegrationTest.java. Implement end-to-end tests for all transaction types (fund transfers, debits, credits) with atomic operation and rollback scenario verification. Verify balance reconciliation with PROCTRAN audit records and performance under load. No TransactionIntegrationTest.java exists yet."
        }
    ],
    
    "summary": {
        "total_cobol_programs": 29,
        "completed_programs": 14,
        "completed_breakdown": {
            "ui_layer_programs": 9,  # BNK1* BMS screens replaced by REST APIs
            "migrated_utilities": 5   # CRDTAGY1-5 (1 service), GETCOMPY, GETSCODE, ABNDPROC, BANKDATA
        },
        "remaining_to_migrate": 11,  # Business logic programs
        "total_tasks": 23,
        "setup_tasks": 3,
        "validator_tasks": 9,
        "migration_tasks": 8,
        "integration_tasks": 3,
        "estimated_total_hours": 190  # Sum of all task estimates
    },
    
    "completed_programs": [
        "BNKMENU",   # Main menu screen
        "BNK1TFN",   # Transfer funds screen
        "BNK1CCS",   # Customer screen
        "BNK1CCA",   # List customer accounts screen
        "BNK1CAC",   # Create account screen
        "BNK1UAC",   # Update account screen
        "BNK1CRA",   # Create account alternate screen
        "BNK1DCS",   # Delete customer screen
        "BNK1DAC",   # Delete account screen
        
        "CRDTAGY1",  # Credit agency 1 -> CreditAgencyService
        "CRDTAGY2",  # Credit agency 2 -> CreditAgencyService
        "CRDTAGY3",  # Credit agency 3 -> CreditAgencyService
        "CRDTAGY4",  # Credit agency 4 -> CreditAgencyService
        "CRDTAGY5",  # Credit agency 5 -> CreditAgencyService
        "GETCOMPY",  # Get company info -> CompanyInfoService
        "GETSCODE",  # Get sort code -> SortCodeService
        "ABNDPROC",  # Error processing -> ErrorLoggingService
        "BANKDATA"   # Data generator -> BankDataGenerator
    ],
    
    "programs_to_migrate": [
        {"program": "CRECUST", "task": "migrate_002", "lines": 1440, "complexity": "high"},
        {"program": "INQCUST", "task": "migrate_001", "lines": 712, "complexity": "medium"},
        {"program": "UPDCUST", "task": "migrate_003", "lines": 365, "complexity": "low"},
        {"program": "DELCUS",  "task": "migrate_003", "lines": 762, "complexity": "medium"},
        
        {"program": "CREACC",  "task": "migrate_005", "lines": 1248, "complexity": "high"},
        {"program": "INQACC",  "task": "migrate_004", "lines": 1003, "complexity": "medium"},
        {"program": "INQACCCU","task": "migrate_004", "lines": 883, "complexity": "medium"},
        {"program": "UPDACC",  "task": "migrate_006", "lines": 407, "complexity": "low"},
        {"program": "DELACC",  "task": "migrate_006", "lines": 650, "complexity": "medium"},
        
        {"program": "XFRFUN",  "task": "migrate_007", "lines": 1925, "complexity": "high"},
        {"program": "DBCRFUN", "task": "migrate_008", "lines": 862, "complexity": "medium"}
    ],
    
    "architecture_notes": {
        "ui_layer_strategy": "All 9 BNK1* BMS 3270 screen programs are replaced by REST APIs in Spring Boot. No direct migration needed.",
        "credit_agency_consolidation": "All 5 CRDTAGY programs are identical dummy credit agencies, consolidated into single CreditAgencyService.",
        "grouping_rationale": {
            "migrate_003": "UPDCUST (365 lines) + DELCUS (762 lines) grouped as complementary customer write operations",
            "migrate_004": "INQACC (1003 lines) + INQACCCU (883 lines) grouped as account read operations with similar cursor patterns",
            "migrate_006": "UPDACC (407 lines) + DELACC (650 lines) grouped as complementary account write operations"
        },
        "standalone_tasks": {
            "migrate_002": "CRECUST alone due to complexity (1440 lines, async credit checks, Named Counter)",
            "migrate_005": "CREACC alone due to complexity (1248 lines, Named Counter, account number generation)",
            "migrate_007": "XFRFUN alone due to high complexity (1925 lines, dual-account updates, rollback handling)"
        },
        "data_access_patterns": {
            "vsam": "Customer records use VSAM with Named Counters for customer number generation",
            "db2": "Account and Transaction records use DB2 with cursor-based pagination",
            "proctran": "Audit trail for all create/update/delete operations except UPDCUST"
        },
        "transaction_boundaries": {
            "single_entity": "CRECUST, CREACC, INQCUST, INQACC - operate on single entity",
            "cascade": "DELCUS deletes customer then all associated accounts",
            "dual_entity": "XFRFUN updates two accounts (debit source, credit target) atomically"
        }
    }
}
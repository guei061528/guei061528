# Database Schema Design for JIRA Test History

## Overview

This document describes the database schema for storing JIRA test history, replacing the local JSON file storage (`~/.jira_test_history.json`).

## Database Tables

### 1. test_history (Main Table)

Stores the historical test results for degrade detection.

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each record |
| `test_key` | VARCHAR(255) | NOT NULL, INDEX | Unique test identifier: `{chipset}_{Model}_{TestcaseName}` |
| `last_result` | VARCHAR(10) | NOT NULL | Last test result: 'PASS' or 'FAIL' |
| `last_version` | VARCHAR(50) | NULL | Last image version (e.g., '808') |
| `last_db` | VARCHAR(50) | NULL | Last daily build number (e.g., 'DB2188') |
| `last_fail_hash` | VARCHAR(32) | NULL | MD5 hash of the normalized fail reason |
| `last_jira_key` | VARCHAR(50) | NULL, INDEX | Last created JIRA issue key (e.g., 'MA-12345') |
| `last_updated` | VARCHAR(500) | NULL | Jenkins URL or timestamp of last update |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Record update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `test_key` (for fast lookup)
- INDEX on `last_jira_key` (for searching by JIRA key)
- INDEX on `last_result` (for filtering by result)
- INDEX on `updated_at` (for time-based queries)

**Example Record:**
```json
{
  "id": 1,
  "test_key": "MacArthur7P_DEMETER_test_ccc_11_21_str_dtv",
  "last_result": "FAIL",
  "last_version": "808",
  "last_db": "DB2188",
  "last_fail_hash": "a3779704b9cd17a8f677159ef8c1a194",
  "last_jira_key": "MA-12345",
  "last_updated": "http://jenkins.example.com/job/test/123/",
  "created_at": "2025-12-18 05:14:53",
  "updated_at": "2025-12-18 05:14:53"
}
```

---

### 2. test_history_log (Optional - Historical Tracking)

Stores complete history of all test runs (optional table for trend analysis).

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `test_key` | VARCHAR(255) | NOT NULL, INDEX | Test identifier |
| `result` | VARCHAR(10) | NOT NULL | Test result: 'PASS' or 'FAIL' |
| `version` | VARCHAR(50) | NULL | Image version |
| `db_number` | VARCHAR(50) | NULL | Daily build number |
| `fail_hash` | VARCHAR(32) | NULL | MD5 hash of fail reason (if FAIL) |
| `fail_detail` | TEXT | NULL | Full fail log detail |
| `jira_key` | VARCHAR(50) | NULL, INDEX | JIRA issue key (if created) |
| `jenkins_url` | VARCHAR(500) | NULL | Jenkins job URL |
| `chipset` | VARCHAR(100) | NULL, INDEX | IC name/chipset |
| `model` | VARCHAR(100) | NULL, INDEX | Device model |
| `test_name` | VARCHAR(255) | NULL | Test case name |
| `is_degrade` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this was marked as degrade |
| `action_taken` | VARCHAR(50) | NULL | Action: 'create_new', 'comment_existing', or NULL |
| `run_timestamp` | TIMESTAMP | NOT NULL, INDEX | When the test was run |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `test_key`
- INDEX on `jira_key`
- INDEX on `chipset`
- INDEX on `model`
- INDEX on `run_timestamp`
- COMPOSITE INDEX on `(test_key, run_timestamp)` for time-series queries

**Example Record:**
```json
{
  "id": 1,
  "test_key": "MacArthur7P_DEMETER_test_ccc_11_21_str_dtv",
  "result": "FAIL",
  "version": "808",
  "db_number": "DB2188",
  "fail_hash": "a3779704b9cd17a8f677159ef8c1a194",
  "fail_detail": "[scaler] MISSING 'RTK Disable Main ForceBG': Failed to disable Main ForceBG.",
  "jira_key": "MA-12345",
  "jenkins_url": "http://jenkins.example.com/job/test/123/",
  "chipset": "MacArthur7P",
  "model": "DEMETER",
  "test_name": "test_ccc_11_21_str_dtv",
  "is_degrade": true,
  "action_taken": "create_new",
  "run_timestamp": "2025-12-18 05:14:53",
  "created_at": "2025-12-18 05:14:53"
}
```

---

## SQL Schema (MySQL/MariaDB)

```sql
-- Main table for current test status
CREATE TABLE test_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_key VARCHAR(255) NOT NULL,
    last_result VARCHAR(10) NOT NULL,
    last_version VARCHAR(50) NULL,
    last_db VARCHAR(50) NULL,
    last_fail_hash VARCHAR(32) NULL,
    last_jira_key VARCHAR(50) NULL,
    last_updated VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_test_key (test_key),
    INDEX idx_jira_key (last_jira_key),
    INDEX idx_result (last_result),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: Historical log table for complete test run history
CREATE TABLE test_history_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    test_key VARCHAR(255) NOT NULL,
    result VARCHAR(10) NOT NULL,
    version VARCHAR(50) NULL,
    db_number VARCHAR(50) NULL,
    fail_hash VARCHAR(32) NULL,
    fail_detail TEXT NULL,
    jira_key VARCHAR(50) NULL,
    jenkins_url VARCHAR(500) NULL,
    chipset VARCHAR(100) NULL,
    model VARCHAR(100) NULL,
    test_name VARCHAR(255) NULL,
    is_degrade BOOLEAN NOT NULL DEFAULT FALSE,
    action_taken VARCHAR(50) NULL,
    run_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_test_key (test_key),
    INDEX idx_jira_key (jira_key),
    INDEX idx_chipset (chipset),
    INDEX idx_model (model),
    INDEX idx_run_timestamp (run_timestamp),
    INDEX idx_test_key_time (test_key, run_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## SQL Schema (PostgreSQL)

```sql
-- Main table for current test status
CREATE TABLE test_history (
    id BIGSERIAL PRIMARY KEY,
    test_key VARCHAR(255) NOT NULL,
    last_result VARCHAR(10) NOT NULL,
    last_version VARCHAR(50),
    last_db VARCHAR(50),
    last_fail_hash VARCHAR(32),
    last_jira_key VARCHAR(50),
    last_updated VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_test_key UNIQUE (test_key)
);

CREATE INDEX idx_test_history_jira_key ON test_history(last_jira_key);
CREATE INDEX idx_test_history_result ON test_history(last_result);
CREATE INDEX idx_test_history_updated ON test_history(updated_at);

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_test_history_updated_at BEFORE UPDATE
ON test_history FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Optional: Historical log table
CREATE TABLE test_history_log (
    id BIGSERIAL PRIMARY KEY,
    test_key VARCHAR(255) NOT NULL,
    result VARCHAR(10) NOT NULL,
    version VARCHAR(50),
    db_number VARCHAR(50),
    fail_hash VARCHAR(32),
    fail_detail TEXT,
    jira_key VARCHAR(50),
    jenkins_url VARCHAR(500),
    chipset VARCHAR(100),
    model VARCHAR(100),
    test_name VARCHAR(255),
    is_degrade BOOLEAN NOT NULL DEFAULT FALSE,
    action_taken VARCHAR(50),
    run_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_history_log_test_key ON test_history_log(test_key);
CREATE INDEX idx_test_history_log_jira_key ON test_history_log(jira_key);
CREATE INDEX idx_test_history_log_chipset ON test_history_log(chipset);
CREATE INDEX idx_test_history_log_model ON test_history_log(model);
CREATE INDEX idx_test_history_log_run_timestamp ON test_history_log(run_timestamp);
CREATE INDEX idx_test_history_log_test_key_time ON test_history_log(test_key, run_timestamp);
```

---

## Database Operations

### 1. Get Test History (for degrade check)

```sql
SELECT test_key, last_result, last_version, last_db, last_fail_hash, last_jira_key, last_updated
FROM test_history
WHERE test_key = ?;
```

### 2. Insert/Update Test History

```sql
-- Insert or update (MySQL)
INSERT INTO test_history (test_key, last_result, last_version, last_db, last_fail_hash, last_jira_key, last_updated)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
    last_result = VALUES(last_result),
    last_version = VALUES(last_version),
    last_db = VALUES(last_db),
    last_fail_hash = VALUES(last_fail_hash),
    last_jira_key = VALUES(last_jira_key),
    last_updated = VALUES(last_updated);

-- Insert or update (PostgreSQL)
INSERT INTO test_history (test_key, last_result, last_version, last_db, last_fail_hash, last_jira_key, last_updated)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (test_key) DO UPDATE SET
    last_result = EXCLUDED.last_result,
    last_version = EXCLUDED.last_version,
    last_db = EXCLUDED.last_db,
    last_fail_hash = EXCLUDED.last_fail_hash,
    last_jira_key = EXCLUDED.last_jira_key,
    last_updated = EXCLUDED.last_updated;
```

### 3. Insert Historical Log (optional)

```sql
INSERT INTO test_history_log 
(test_key, result, version, db_number, fail_hash, fail_detail, jira_key, jenkins_url, 
 chipset, model, test_name, is_degrade, action_taken, run_timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

### 4. Query Recent Degrades

```sql
SELECT * FROM test_history_log
WHERE is_degrade = TRUE
  AND run_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY run_timestamp DESC;
```

### 5. Query Test Trend

```sql
SELECT test_key, result, version, db_number, run_timestamp
FROM test_history_log
WHERE test_key = ?
ORDER BY run_timestamp DESC
LIMIT 10;
```

---

## Connection Configuration

### Database Connection Parameters

```python
DATABASE_CONFIG = {
    'host': 'localhost',          # Database host
    'port': 3306,                 # Database port (3306 for MySQL, 5432 for PostgreSQL)
    'database': 'jira_test_db',   # Database name
    'user': 'jira_user',          # Database user
    'password': 'password',       # Database password
    'charset': 'utf8mb4',         # Character set
    'pool_size': 5,               # Connection pool size
    'max_overflow': 10,           # Max overflow connections
    'pool_timeout': 30,           # Connection timeout (seconds)
    'pool_recycle': 3600,         # Recycle connections after 1 hour
}
```

### Environment Variables (Recommended)

```bash
export JIRA_DB_HOST=localhost
export JIRA_DB_PORT=3306
export JIRA_DB_NAME=jira_test_db
export JIRA_DB_USER=jira_user
export JIRA_DB_PASSWORD=password
```

---

## Recommended Database Engines

### Option 1: MySQL/MariaDB
- **Pros**: Widely used, good performance, easy to setup
- **Cons**: None for this use case
- **Recommended for**: Production use

### Option 2: PostgreSQL
- **Pros**: Advanced features, better JSON support, excellent for analytics
- **Cons**: Slightly more complex setup
- **Recommended for**: Production use with analytics needs

### Option 3: SQLite (for testing only)
- **Pros**: No server needed, single file
- **Cons**: Not suitable for concurrent writes
- **Recommended for**: Development/testing only

---

## Migration Strategy

### Step 1: Export existing JSON data
```python
import json
from pathlib import Path

history_file = Path.home() / '.jira_test_history.json'
with open(history_file, 'r') as f:
    history = json.load(f)
```

### Step 2: Import to database
```python
for test_key, record in history.items():
    cursor.execute("""
        INSERT INTO test_history (test_key, last_result, last_version, last_db, 
                                  last_fail_hash, last_jira_key, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (test_key, record['last_result'], record['last_version'], 
          record['last_db'], record.get('last_fail_hash'), 
          record.get('last_jira_key'), record['last_updated']))
```

---

## Data Retention Policy (Optional)

```sql
-- Delete historical logs older than 90 days
DELETE FROM test_history_log
WHERE run_timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Archive old data before deletion (optional)
CREATE TABLE test_history_log_archive LIKE test_history_log;

INSERT INTO test_history_log_archive
SELECT * FROM test_history_log
WHERE run_timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

---

## Summary

### Minimal Setup (Recommended to start)
- **Single table**: `test_history` 
- **Database**: MySQL or PostgreSQL
- **Connection**: Via environment variables

### Advanced Setup (Optional)
- **Two tables**: `test_history` + `test_history_log`
- **Benefits**: Complete historical tracking, trend analysis
- **Trade-off**: More storage space, more complex

### Next Steps
1. Choose database engine (MySQL/MariaDB or PostgreSQL)
2. Create database and user
3. Run SQL schema creation scripts
4. Configure database connection in code
5. Migrate existing JSON data (if any)
6. Update `degrade_tracker.py` to use database instead of JSON file


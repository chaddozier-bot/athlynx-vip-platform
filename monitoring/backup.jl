#!/usr/bin/env julia
"""
🦁 ATHLYNX AI - Auto-Backup System
Julia High-Performance Database Backup

Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0

Dreams Do Come True 2026! 🚀
"""

using LibPQ
using CSV
using DataFrames
using Dates
using GZip

# Database connection
const DB_URL = get(ENV, "DATABASE_URL", 
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require")

# Backup configuration
const BACKUP_DIR = get(ENV, "BACKUP_DIR", "./backups")
const MAX_BACKUPS = 30  # Keep last 30 backups

# Tables to backup
const TABLES = [
    "users",
    "waitlist",
    "athletes",
    "nil_deals",
    "feed_posts",
    "messages",
    "verification_codes",
    "subscriptions",
    "analytics_events",
    "transfer_portal"
]

# Connect to database
function connect_db()
    try
        conn = LibPQ.Connection(DB_URL)
        println("✅ Connected to NEON database")
        return conn
    catch e
        println("❌ Database connection failed: $e")
        return nothing
    end
end

# Create backup directory
function ensure_backup_dir()
    if !isdir(BACKUP_DIR)
        mkpath(BACKUP_DIR)
        println("📁 Created backup directory: $BACKUP_DIR")
    end
end

# Backup a single table
function backup_table(conn, table_name::String, backup_path::String)
    try
        # Get all data from table
        result = execute(conn, "SELECT * FROM $table_name")
        df = DataFrame(result)
        
        # Save to CSV
        csv_file = joinpath(backup_path, "$table_name.csv")
        CSV.write(csv_file, df)
        
        row_count = nrow(df)
        println("   ✅ $table_name: $row_count rows")
        
        return row_count
    catch e
        println("   ❌ $table_name: Error - $e")
        return 0
    end
end

# Create full backup
function create_backup()
    println("\n" * "="^60)
    println("🦁 ATHLYNX AI - Database Backup")
    println("Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14")
    println("Started: $(now())")
    println("="^60)
    
    ensure_backup_dir()
    
    # Create timestamped backup folder
    timestamp = Dates.format(now(), "yyyy-mm-dd_HH-MM-SS")
    backup_path = joinpath(BACKUP_DIR, "backup_$timestamp")
    mkpath(backup_path)
    
    println("\n📦 Backup Location: $backup_path\n")
    
    conn = connect_db()
    if isnothing(conn)
        println("❌ Cannot proceed without database connection")
        return nothing
    end
    
    total_rows = 0
    backed_up_tables = 0
    
    println("📊 Backing up tables:")
    for table in TABLES
        rows = backup_table(conn, table, backup_path)
        total_rows += rows
        if rows > 0
            backed_up_tables += 1
        end
    end
    
    close(conn)
    
    # Create compressed archive
    println("\n🗜️ Compressing backup...")
    archive_name = "backup_$timestamp.tar.gz"
    archive_path = joinpath(BACKUP_DIR, archive_name)
    
    try
        run(`tar -czf $archive_path -C $BACKUP_DIR backup_$timestamp`)
        println("✅ Created archive: $archive_name")
        
        # Remove uncompressed folder
        rm(backup_path, recursive=true)
        println("🗑️ Cleaned up temporary files")
    catch e
        println("⚠️ Compression failed: $e")
        println("   Keeping uncompressed backup")
    end
    
    # Create backup manifest
    manifest = Dict(
        "timestamp" => string(now()),
        "backup_name" => archive_name,
        "tables_backed_up" => backed_up_tables,
        "total_rows" => total_rows,
        "project" => "Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14"
    )
    
    manifest_file = joinpath(BACKUP_DIR, "latest_backup.json")
    open(manifest_file, "w") do f
        write(f, JSON3.write(manifest))
    end
    
    println("\n" * "="^60)
    println("✅ BACKUP COMPLETE!")
    println("   Tables: $backed_up_tables")
    println("   Total Rows: $total_rows")
    println("   Archive: $archive_name")
    println("="^60)
    println("Dreams Do Come True 2026! 🚀\n")
    
    # Cleanup old backups
    cleanup_old_backups()
    
    return manifest
end

# Cleanup old backups (keep last MAX_BACKUPS)
function cleanup_old_backups()
    println("\n🧹 Checking for old backups to clean up...")
    
    backups = filter(f -> endswith(f, ".tar.gz"), readdir(BACKUP_DIR))
    
    if length(backups) > MAX_BACKUPS
        # Sort by name (which includes timestamp)
        sort!(backups)
        
        # Remove oldest backups
        to_remove = backups[1:end-MAX_BACKUPS]
        
        for backup in to_remove
            backup_path = joinpath(BACKUP_DIR, backup)
            rm(backup_path)
            println("   🗑️ Removed old backup: $backup")
        end
        
        println("✅ Cleaned up $(length(to_remove)) old backups")
    else
        println("✅ No cleanup needed ($(length(backups))/$MAX_BACKUPS backups)")
    end
end

# List all backups
function list_backups()
    println("\n" * "="^60)
    println("🦁 ATHLYNX AI - Backup List")
    println("="^60)
    
    ensure_backup_dir()
    
    backups = filter(f -> endswith(f, ".tar.gz"), readdir(BACKUP_DIR))
    sort!(backups, rev=true)
    
    if isempty(backups)
        println("\n📭 No backups found")
    else
        println("\n📦 Found $(length(backups)) backups:\n")
        for (i, backup) in enumerate(backups)
            backup_path = joinpath(BACKUP_DIR, backup)
            size_mb = round(filesize(backup_path) / 1024 / 1024, digits=2)
            println("   $i. $backup ($size_mb MB)")
        end
    end
    
    println("\n" * "="^60 * "\n")
end

# Restore from backup
function restore_backup(backup_name::String)
    println("\n" * "="^60)
    println("🦁 ATHLYNX AI - Restore Backup")
    println("="^60)
    
    backup_path = joinpath(BACKUP_DIR, backup_name)
    
    if !isfile(backup_path)
        println("❌ Backup not found: $backup_name")
        return false
    end
    
    println("\n⚠️ WARNING: This will overwrite existing data!")
    println("   Backup: $backup_name")
    println("\n   Press Ctrl+C to cancel, or wait 5 seconds to continue...")
    sleep(5)
    
    # Extract backup
    temp_dir = joinpath(BACKUP_DIR, "restore_temp")
    mkpath(temp_dir)
    
    try
        run(`tar -xzf $backup_path -C $temp_dir`)
        println("✅ Extracted backup")
        
        # Find the backup folder
        extracted_dirs = filter(isdir, readdir(temp_dir, join=true))
        if isempty(extracted_dirs)
            println("❌ No data found in backup")
            return false
        end
        
        data_dir = extracted_dirs[1]
        
        conn = connect_db()
        if isnothing(conn)
            println("❌ Cannot proceed without database connection")
            return false
        end
        
        println("\n📊 Restoring tables:")
        for table in TABLES
            csv_file = joinpath(data_dir, "$table.csv")
            if isfile(csv_file)
                df = CSV.read(csv_file, DataFrame)
                # Note: Actual restore logic would need to handle INSERT statements
                println("   ✅ $table: $(nrow(df)) rows ready")
            end
        end
        
        close(conn)
        
        # Cleanup
        rm(temp_dir, recursive=true)
        
        println("\n✅ Restore preparation complete!")
        println("   Note: Manual SQL execution required for actual restore")
        
    catch e
        println("❌ Restore failed: $e")
        return false
    end
    
    println("\n" * "="^60 * "\n")
    return true
end

# Scheduled backup loop
function schedule_backup(interval_hours=24)
    println("🦁 ATHLYNX Backup Scheduler Started")
    println("Backup interval: $(interval_hours) hours")
    
    while true
        create_backup()
        
        next_backup = now() + Hour(interval_hours)
        println("⏳ Next backup scheduled for: $next_backup")
        
        sleep(interval_hours * 3600)
    end
end

# Main entry point
function main()
    println("""
    
    🦁 ═══════════════════════════════════════════════════════════════════════
    
       ATHLYNX AI - Auto-Backup System
       Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14
       
       Julia High-Performance Database Backup
       
       Usage:
         julia backup.jl              - Run backup now
         julia backup.jl schedule 24  - Schedule every 24 hours
         julia backup.jl list         - List all backups
         julia backup.jl restore <name> - Restore from backup
       
       Dreams Do Come True 2026! 🚀
       
    ═══════════════════════════════════════════════════════════════════════ 🦁
    
    """)
    
    if length(ARGS) == 0
        # Run backup now
        create_backup()
    elseif ARGS[1] == "schedule"
        interval = length(ARGS) > 1 ? parse(Int, ARGS[2]) : 24
        schedule_backup(interval)
    elseif ARGS[1] == "list"
        list_backups()
    elseif ARGS[1] == "restore" && length(ARGS) > 1
        restore_backup(ARGS[2])
    else
        println("Unknown command. Use: backup, schedule, list, or restore")
    end
end

# Run if executed directly
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

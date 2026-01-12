#!/usr/bin/env julia
"""
🦁 ATHLYNX AI - System Health Monitor
Julia High-Performance Health Checking

Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0

Dreams Do Come True 2026! 🚀
"""

using LibPQ
using HTTP
using JSON3
using Dates

# Database connection
const DB_URL = get(ENV, "DATABASE_URL", 
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require")

# API endpoint
const API_URL = get(ENV, "API_URL", "http://localhost:8000")

# Alert thresholds
const THRESHOLDS = Dict(
    "db_response_time_ms" => 1000,      # 1 second
    "api_response_time_ms" => 2000,     # 2 seconds
    "disk_usage_percent" => 80,          # 80%
    "memory_usage_percent" => 85,        # 85%
    "error_rate_percent" => 5            # 5%
)

# Health status structure
mutable struct HealthStatus
    timestamp::DateTime
    database_healthy::Bool
    database_response_ms::Float64
    api_healthy::Bool
    api_response_ms::Float64
    disk_usage_percent::Float64
    memory_usage_percent::Float64
    alerts::Vector{String}
end

# Check database health
function check_database_health()
    start_time = time()
    
    try
        conn = LibPQ.Connection(DB_URL)
        
        # Simple query to test connection
        result = execute(conn, "SELECT 1 as test, NOW() as server_time")
        data = fetch!(result)
        
        close(conn)
        
        response_time = (time() - start_time) * 1000  # Convert to ms
        
        return true, response_time
    catch e
        response_time = (time() - start_time) * 1000
        println("❌ Database health check failed: $e")
        return false, response_time
    end
end

# Check API health
function check_api_health()
    start_time = time()
    
    try
        response = HTTP.get("$API_URL/api/health", timeout=10)
        response_time = (time() - start_time) * 1000
        
        if response.status == 200
            return true, response_time
        else
            return false, response_time
        end
    catch e
        response_time = (time() - start_time) * 1000
        println("⚠️ API health check failed: $e")
        return false, response_time
    end
end

# Check disk usage (Linux/macOS)
function check_disk_usage()
    try
        output = read(`df -h /`, String)
        lines = split(output, '\n')
        if length(lines) > 1
            parts = split(lines[2])
            if length(parts) >= 5
                usage_str = replace(parts[5], "%" => "")
                return parse(Float64, usage_str)
            end
        end
        return 0.0
    catch e
        println("⚠️ Disk usage check failed: $e")
        return 0.0
    end
end

# Check memory usage (Linux)
function check_memory_usage()
    try
        output = read(`free -m`, String)
        lines = split(output, '\n')
        if length(lines) > 1
            parts = split(lines[2])
            if length(parts) >= 3
                total = parse(Float64, parts[2])
                used = parse(Float64, parts[3])
                return (used / total) * 100
            end
        end
        return 0.0
    catch e
        # Try macOS approach
        try
            output = read(`vm_stat`, String)
            # Parse macOS memory stats
            return 50.0  # Placeholder
        catch
            println("⚠️ Memory usage check failed: $e")
            return 0.0
        end
    end
end

# Generate alerts based on thresholds
function generate_alerts(status::HealthStatus)
    alerts = String[]
    
    if !status.database_healthy
        push!(alerts, "🚨 CRITICAL: Database is DOWN!")
    elseif status.database_response_ms > THRESHOLDS["db_response_time_ms"]
        push!(alerts, "⚠️ WARNING: Database response slow ($(round(status.database_response_ms, digits=0))ms)")
    end
    
    if !status.api_healthy
        push!(alerts, "🚨 CRITICAL: API is DOWN!")
    elseif status.api_response_ms > THRESHOLDS["api_response_time_ms"]
        push!(alerts, "⚠️ WARNING: API response slow ($(round(status.api_response_ms, digits=0))ms)")
    end
    
    if status.disk_usage_percent > THRESHOLDS["disk_usage_percent"]
        push!(alerts, "⚠️ WARNING: Disk usage high ($(round(status.disk_usage_percent, digits=1))%)")
    end
    
    if status.memory_usage_percent > THRESHOLDS["memory_usage_percent"]
        push!(alerts, "⚠️ WARNING: Memory usage high ($(round(status.memory_usage_percent, digits=1))%)")
    end
    
    return alerts
end

# Run full health check
function run_health_check()
    println("\n" * "="^60)
    println("🦁 ATHLYNX AI - System Health Check")
    println("Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14")
    println("Timestamp: $(now())")
    println("="^60)
    
    # Initialize status
    status = HealthStatus(
        now(),
        false, 0.0,
        false, 0.0,
        0.0, 0.0,
        String[]
    )
    
    # Check database
    println("\n🔍 Checking Database...")
    db_healthy, db_time = check_database_health()
    status.database_healthy = db_healthy
    status.database_response_ms = db_time
    
    if db_healthy
        println("   ✅ Database: HEALTHY ($(round(db_time, digits=0))ms)")
    else
        println("   ❌ Database: DOWN")
    end
    
    # Check API
    println("\n🔍 Checking API...")
    api_healthy, api_time = check_api_health()
    status.api_healthy = api_healthy
    status.api_response_ms = api_time
    
    if api_healthy
        println("   ✅ API: HEALTHY ($(round(api_time, digits=0))ms)")
    else
        println("   ⚠️ API: UNREACHABLE (may not be running)")
    end
    
    # Check system resources
    println("\n🔍 Checking System Resources...")
    status.disk_usage_percent = check_disk_usage()
    status.memory_usage_percent = check_memory_usage()
    
    println("   💾 Disk Usage: $(round(status.disk_usage_percent, digits=1))%")
    println("   🧠 Memory Usage: $(round(status.memory_usage_percent, digits=1))%")
    
    # Generate alerts
    status.alerts = generate_alerts(status)
    
    # Display alerts
    if !isempty(status.alerts)
        println("\n" * "="^60)
        println("🚨 ALERTS:")
        for alert in status.alerts
            println("   $alert")
        end
    end
    
    # Overall status
    println("\n" * "="^60)
    overall_healthy = status.database_healthy && isempty(filter(a -> startswith(a, "🚨"), status.alerts))
    
    if overall_healthy
        println("✅ OVERALL STATUS: HEALTHY")
    else
        println("❌ OVERALL STATUS: ISSUES DETECTED")
    end
    
    println("="^60)
    println("Dreams Do Come True 2026! 🚀\n")
    
    return status
end

# Save health status to file
function save_health_status(status::HealthStatus)
    data = Dict(
        "timestamp" => string(status.timestamp),
        "database_healthy" => status.database_healthy,
        "database_response_ms" => status.database_response_ms,
        "api_healthy" => status.api_healthy,
        "api_response_ms" => status.api_response_ms,
        "disk_usage_percent" => status.disk_usage_percent,
        "memory_usage_percent" => status.memory_usage_percent,
        "alerts" => status.alerts,
        "project" => "Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14"
    )
    
    filename = "health_$(Dates.format(now(), "yyyy-mm-dd_HH-MM-SS")).json"
    open(filename, "w") do f
        write(f, JSON3.write(data))
    end
    
    println("📝 Health status saved to $filename")
end

# Continuous monitoring loop
function monitor(interval_seconds=60)
    println("🦁 ATHLYNX Health Monitor Started")
    println("Check interval: $(interval_seconds) seconds")
    
    while true
        status = run_health_check()
        
        # Save status if there are alerts
        if !isempty(status.alerts)
            save_health_status(status)
        end
        
        println("⏳ Next check in $(interval_seconds) seconds...")
        sleep(interval_seconds)
    end
end

# Main entry point
function main()
    println("""
    
    🦁 ═══════════════════════════════════════════════════════════════════════
    
       ATHLYNX AI - System Health Monitor
       Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14
       
       Julia High-Performance Health Checking
       
       Usage:
         julia health.jl              - Run health check once
         julia health.jl monitor 60   - Monitor every 60 seconds
       
       Dreams Do Come True 2026! 🚀
       
    ═══════════════════════════════════════════════════════════════════════ 🦁
    
    """)
    
    if length(ARGS) > 0 && ARGS[1] == "monitor"
        interval = length(ARGS) > 1 ? parse(Int, ARGS[2]) : 60
        monitor(interval)
    else
        status = run_health_check()
        save_health_status(status)
    end
end

# Run if executed directly
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

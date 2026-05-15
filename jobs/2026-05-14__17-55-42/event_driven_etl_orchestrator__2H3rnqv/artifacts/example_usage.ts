/**
 * Example usage of the ETL Orchestrator workflow
 * 
 * This file demonstrates how to call the etl_orchestrator workflow
 * with sample event data.
 */

import { main as etlOrchestrator } from "./etl_orchestrator";

// Example 1: Basic usage with default warehouse target
async function example1() {
  const events = [
    {
      id: "evt_001",
      type: "user_signup",
      payload: {
        userId: "user123",
        email: "user@example.com",
        timestamp: "2026-05-15T00:00:00Z"
      }
    },
    {
      id: "evt_002",
      type: "purchase",
      payload: {
        userId: "user123",
        amount: 99.99,
        currency: "USD",
        productId: "prod_456"
      }
    }
  ];

  const result = await etlOrchestrator(events);
  console.log("Result:", result);
}

// Example 2: With custom warehouse target
async function example2() {
  const events = [
    {
      id: "evt_003",
      type: "page_view",
      payload: {
        userId: "user789",
        page: "/products",
        referrer: "google.com"
      }
    }
  ];

  const result = await etlOrchestrator(events, "staging");
  console.log("Result:", result);
}

// Example 3: Handling duplicates
async function example3() {
  // First run - new events
  const events1 = [
    { id: "evt_100", type: "click", payload: { element: "button" } },
    { id: "evt_101", type: "click", payload: { element: "link" } }
  ];
  
  console.log("First run:");
  const result1 = await etlOrchestrator(events1);
  console.log(result1);
  // This will process 2 new events

  // Second run - includes duplicates
  const events2 = [
    { id: "evt_100", type: "click", payload: { element: "button" } }, // duplicate
    { id: "evt_102", type: "scroll", payload: { depth: 50 } }          // new
  ];
  
  console.log("\nSecond run:");
  const result2 = await etlOrchestrator(events2);
  console.log(result2);
  // This will skip 1 duplicate and process 1 new event
}

// Example 4: Batch processing
async function example4() {
  const events = Array.from({ length: 12 }, (_, i) => ({
    id: `evt_batch_${i}`,
    type: i % 2 === 0 ? "user_action" : "system_event",
    payload: {
      index: i,
      timestamp: new Date(Date.now() - i * 1000).toISOString()
    }
  }));

  const result = await etlOrchestrator(events, "production");
  console.log("Processed batch of 12 events");
  console.log(result);
  // Will enrich in parallel with max 5 concurrent
}

// Example 5: Empty events array
async function example5() {
  const events: any[] = [];
  
  const result = await etlOrchestrator(events);
  console.log("No events to process:", result);
  // Returns success with 0 new events
}

// Example 6: All duplicates
async function example6() {
  // Assume evt_100 and evt_101 were already processed
  const events = [
    { id: "evt_100", type: "click", payload: { element: "button" } },
    { id: "evt_101", type: "click", payload: { element: "link" } }
  ];
  
  const result = await etlOrchestrator(events);
  console.log("All events were duplicates:", result);
  // Returns success with 0 new events, 2 duplicates skipped
}

// Run examples
async function runExamples() {
  console.log("=== ETL Orchestrator Examples ===\n");
  
  // Uncomment to run specific examples
  
  // await example1();
  // await example2();
  // await example3();
  // await example4();
  // await example5();
  // await example6();
  
  console.log("\n=== Examples Complete ===");
}

// Export for use in other modules
export {
  example1,
  example2,
  example3,
  example4,
  example5,
  example6,
  runExamples
};
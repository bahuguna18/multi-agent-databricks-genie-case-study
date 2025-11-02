# Architecture Documentation

## System Architecture

Overview of the multi-agent system architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Query                                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Coordinator Agent  │
                    │   (LangChain ReAct)  │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Sales Agent  │  │Customer Agent│  │  (Both)      │
        │  (LangChain) │  │  (LangChain) │  │              │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                  │                  │
               ▼                  ▼                  ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │Base Genie    │  │Base Genie    │  │  (Delegates) │
        │Agent         │  │Agent         │  │              │
        └──────┬───────┘  └──────┬───────┘  └──────────────┘
               │                  │
               ▼                  ▼
        ┌──────────────┐  ┌──────────────┐
        │Sales Analytics│  │Customer Insights│
        │Genie Space    │  │Genie Space      │
        │(Databricks)   │  │(Databricks)     │
        └──────────────┘  └──────────────────┘
```
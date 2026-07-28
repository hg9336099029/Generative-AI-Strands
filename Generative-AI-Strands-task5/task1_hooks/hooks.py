# Hooks are a mechanism in the Strands framework that allows developers to 
# execute custom code automatically at different stages of an agent's execution 
# lifecycle. They let you observe, modify, validate, log, or control the agent's 
# behavior without changing the agent's core logic.

# In simple terms:

# Hooks are event listeners that run automatically whenever a specific lifecycle event 
# occurs inside a Strands agent.

# Why are Hooks Used?

# Hooks make it possible to add functionality around the agent's execution, such as:

# Logging
# Monitoring
# Validation
# Security checks
# Auditing
# Guardrails
# Performance measurement
# Debugging
# Custom preprocessing
# Custom postprocessing

# Instead of modifying the agent itself, you attach hooks that execute automatically 
# when certain events occur.

import datetime
from strands.hooks import (
    HookProvider, HookRegistry,
    BeforeToolCallEvent, AfterToolCallEvent, MessageAddedEvent,
    BeforeInvocationEvent, AfterInvocationEvent,
    BeforeModelCallEvent, AfterModelCallEvent, AgentInitializedEvent
)

class LifecycleLogger(HookProvider):
    def log(self, event_name: str):
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{timestamp}] {event_name}")

    def register_hooks(self, registry: HookRegistry) -> None:
        # Register all core lifecycle callbacks
        registry.add_callback(AgentInitializedEvent, self.on_init)
        registry.add_callback(BeforeInvocationEvent, self.on_invoke_start)
        registry.add_callback(BeforeModelCallEvent, self.on_model_start)
        registry.add_callback(MessageAddedEvent, self.on_message)
        registry.add_callback(BeforeToolCallEvent, self.pre_tool)
        registry.add_callback(AfterToolCallEvent, self.post_tool)
        registry.add_callback(AfterModelCallEvent, self.on_model_end)
        registry.add_callback(AfterInvocationEvent, self.on_invoke_end)

    def on_init(self, event: AgentInitializedEvent) -> None:
        self.log("AgentInitializedEvent")

    def on_invoke_start(self, event: BeforeInvocationEvent) -> None:
        self.log("BeforeInvocationEvent")

    def on_model_start(self, event: BeforeModelCallEvent) -> None:
        self.log("BeforeModelCallEvent")

    def on_message(self, event: MessageAddedEvent) -> None:
        self.log("MessageAddedEvent")

    # Modifying behaviour: Block tool call if validation fails
    def pre_tool(self, event: BeforeToolCallEvent) -> None:
        self.log(f"BeforeToolCallEvent (Tool: {event.tool_use['name']})")
        
        # Guardrail rule: block access to the 'admin' user
        if 'admin' in str(event.tool_use.get('input', '')).lower():
            self.log("GUARDRAIL TRIGGERED: Blocking tool call.")
            # Cancels the tool call before it runs
            event.cancel_tool = "Access Denied: Cannot fetch data for admin accounts."

    def post_tool(self, event: AfterToolCallEvent) -> None:
        self.log("AfterToolCallEvent")

    def on_model_end(self, event: AfterModelCallEvent) -> None:
        self.log("AfterModelCallEvent")

    def on_invoke_end(self, event: AfterInvocationEvent) -> None:
        self.log("AfterInvocationEvent")
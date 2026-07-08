"""
Advanced example using Flow Builder.

This example demonstrates:
- Creating flows with fluent builder
- Using flow templates
- Executing predefined flows
"""

from lib.engine import DixEngine
from lib.flow_builder import FlowBuilder


def flow_builder_example():
    """Example using the fluent Flow Builder."""
    
    engine = DixEngine()
    
    try:
        engine.connect()
        
        # Create a login flow using fluent builder
        login_flow = (engine.create_flow("Login Flow")
            .open_app("com.example.app")
            .wait_for(text="Login", timeout=10)
            .click(text="Entrar")
            .fill_field(label="Username", value="test_user")
            .fill_field(label="Password", value="test_pass")
            .click(text="Submit")
            .wait_for(text="Welcome")
            .screenshot("login_success")
            .build())
        
        # Execute the flow
        print("Executing login flow...")
        engine.flow.execute(login_flow)
        
        print("Flow completed!")
        
    except Exception as e:
        print(f"Flow execution error: {e}")
        
    finally:
        engine.disconnect()


def flow_template_example():
    """Example using predefined flow templates."""
    
    engine = DixEngine()
    
    try:
        engine.connect()
        
        # List available templates
        templates = engine.list_templates()
        print(f"Available templates: {templates}")
        
        # Use a login template (if available)
        login_steps = engine.use_template(
            "login",
            package="com.example.app",
            username="demo_user",
            password="demo_pass"
        )
        
        if login_steps:
            print("Executing template flow...")
            engine.flow.execute(login_steps)
            
    except Exception as e:
        print(f"Template execution error: {e}")
        
    finally:
        engine.disconnect()


def json_flow_example():
    """Example loading and executing a JSON flow."""
    
    engine = DixEngine()
    
    try:
        engine.connect()
        
        # Load flow from JSON file
        flow_path = "flows/saved_flow.json"
        print(f"Loading flow from {flow_path}...")
        
        flow = engine.flow.load_from_json(flow_path)
        
        if flow:
            print("Executing JSON flow...")
            engine.flow.execute(flow)
            
    except Exception as e:
        print(f"JSON flow execution error: {e}")
        
    finally:
        engine.disconnect()


if __name__ == "__main__":
    # Choose which example to run
    print("=== Flow Builder Example ===")
    flow_builder_example()
    
    print("\n=== Flow Template Example ===")
    flow_template_example()
    
    print("\n=== JSON Flow Example ===")
    json_flow_example()

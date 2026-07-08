"""
Flow Recorder and Builder Demo - Examples of creating flows programmatically.

This demo shows how to use FlowBuilder, Flow Templates, and FlowRecorder
to create automation flows without manually writing JSON files.
"""

import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.flow_builder import flow, FlowBuilder
from lib.flow_templates import get_template, list_templates
from lib.recorder import FlowRecorder


def demo_flow_builder():
    """Demonstrate the fluent FlowBuilder API."""
    print("\n" + "="*60)
    print("DEMO: FlowBuilder - Fluent Interface")
    print("="*60)
    
    # Create a flow using fluent interface
    login_flow = (flow("login_demo")
        .open_app("com.example.app")
        .wait_for(text="Bem-vindo", timeout=10)
        .click(text="Já tenho uma conta")
        .wait_for(text="Forma de entrar", timeout=5)
        .click(desc="CPF")
        .fill(label="Número de CPF", value="02959350146", field_type="cpf")
        .fill(label="Senha", value="MinhaSenha123!", field_type="password")
        .screenshot("pre_login")
        .click(text="Entrar")
        .wait_for(text="Home", timeout=10)
        .assert_exists(text="Home")
        .screenshot("post_login")
        .build())
    
    print(f"\nCreated flow with {len(login_flow)} steps:")
    for i, step in enumerate(login_flow, 1):
        action = step.get('action', 'unknown')
        print(f"  {i}. {action}")
    
    # Save flow to JSON
    builder = flow("saved_flow")
    builder.open_app("com.app.test")
    builder.click(text="Inicio")
    builder.fill(label="Nome", value="Teste")
    builder.screenshot("resultado")
    
    saved_path = builder.save()
    print(f"\nSaved flow to: {saved_path}")
    
    return login_flow


def demo_flow_templates():
    """Demonstrate using pre-built flow templates."""
    print("\n" + "="*60)
    print("DEMO: Flow Templates - Reusable Patterns")
    print("="*60)
    
    # List available templates
    templates = list_templates()
    print(f"\nAvailable templates ({len(templates)}):")
    for t in templates[:10]:  # Show first 10
        print(f"  - {t}")
    if len(templates) > 10:
        print(f"  ... and {len(templates) - 10} more")
    
    # Use login template
    login = get_template(
        "login",
        package="com.meu.app",
        cpf="02959350146",
        password="Senha123!"
    )
    
    print(f"\nLogin template generated {len(login)} steps")
    
    # Use registration template
    registration = get_template(
        "registration_cpf",
        cpf="02959350146",
        full_name="João Silva",
        email="joao@example.com",
        phone="11999999999",
        password="Senha123!"
    )
    
    print(f"Registration template generated {len(registration)} steps")
    
    # Use payment template
    payment = get_template(
        "payment_card",
        package="com.meu.app",
        card_number="4111111111111111",
        card_holder="JOAO SILVA",
        expiry_date="12/25",
        cvv="123",
        installments=3
    )
    
    print(f"Payment template generated {len(payment)} steps")
    
    return login, registration, payment


def demo_flow_composition():
    """Demonstrate composing flows from multiple templates."""
    print("\n" + "="*60)
    print("DEMO: Flow Composition - Combining Templates")
    print("="*60)
    
    # Create a complete test flow by combining templates
    complete_flow = (flow("complete_test")
        # Setup
        .extend(get_template("setup_app", package="com.meu.app"))
        
        # Login
        .extend(get_template("login", 
                           package="com.meu.app",
                           cpf="02959350146",
                           password="Senha123!"))
        
        # Navigate and perform actions
        .click(text="Perfil")
        .click(text="Editar dados")
        
        # Fill personal data
        .extend(get_template("personal_data",
                           name="João Silva",
                           cpf="02959350146",
                           email="joao@example.com",
                           phone="11999999999",
                           birthdate="01/01/1990",
                           cep="01310-100"))
        
        # Verify
        .extend(get_template("verify_login"))
        .extend(get_template("no_errors"))
        
        # Screenshot
        .screenshot("final")
        
        # Teardown
        .extend(get_template("teardown_app", package="com.meu.app"))
        
        .build())
    
    print(f"\nComposed flow with {len(complete_flow)} steps")
    
    return complete_flow


def demo_conditional_flows():
    """Demonstrate conditional logic in flows."""
    print("\n" + "="*60)
    print("DEMO: Conditional Flows - If/Else Logic")
    print("="*60)
    
    # Create flow with conditional logic
    conditional_flow = (flow("conditional_demo")
        .open_app("com.example.app")
        
        # Check if tutorial popup exists
        .if_exists(text="Tutorial")
            .click(text="Pular")
            .screenshot("tutorial_skipped")
        .endif()
        
        # Main flow
        .click(text="Entrar")
        
        # Handle different login methods
        .if_exists(text="Já tenho conta")
            .click(text="Já tenho conta")
        .else_()
            .click(text="Criar conta")
        .endif()
        
        .build())
    
    print(f"\nConditional flow created with nested logic")
    print("Steps include if/else blocks for handling different scenarios")
    
    return conditional_flow


def demo_loop_flows():
    """Demonstrate loops in flows."""
    print("\n" + "="*60)
    print("DEMO: Loop Flows - Repeating Actions")
    print("="*60)
    
    # Create flow with loops
    loop_flow = (flow("loop_demo")
        .open_app("com.example.app")
        
        # Scroll through list items
        .loop(5)
            .swipe(direction="down")
            .wait(0.5)
        .endloop()
        
        # Process each item in a list
        .foreach(["Item 1", "Item 2", "Item 3"], variable="item")
            .click(text="item")  # Would be replaced with actual variable
            .wait(0.3)
        .endloop()
        
        .build())
    
    print(f"\nLoop flow created with repeatable actions")
    
    return loop_flow


def demo_recorder_simulation():
    """Simulate recording actions programmatically."""
    print("\n" + "="*60)
    print("DEMO: FlowRecorder - Recording Actions")
    print("="*60)
    
    # Create a mock engine for demonstration
    class MockEngine:
        pass
    
    mock_engine = MockEngine()
    
    # Simulate recording
    recorder = FlowRecorder(mock_engine)
    recorder.start()
    
    # Record actions (simulating what would be captured)
    recorder.record_open_app("com.example.app")
    recorder.record_wait(2.0)
    recorder.record_click(text="Login", description="Click login button")
    recorder.record_fill(label="CPF", value="02959350146")
    recorder.record_fill(label="Senha", value="******")
    recorder.record_click(text="Entrar")
    recorder.record_wait(3.0)
    recorder.record_screenshot("login_success")
    recorder.record_back()
    
    recorder.stop()
    
    # Print summary
    recorder.print_summary()
    
    # Get flow
    recorded_flow = recorder.build_flow()
    print(f"Recorded flow has {len(recorded_flow)} actions")
    
    # Export to Python code
    python_code = recorder.export_to_python("/workspace/demo_recorded_flow.py")
    print(f"Exported to Python: {python_code}")
    
    return recorder


def main():
    """Run all demos."""
    print("\n" + "#"*60)
    print("# dixUIAuto - Flow Builder & Recorder Demos")
    print("#"*60)
    
    # Run demos
    demo_flow_builder()
    demo_flow_templates()
    demo_flow_composition()
    demo_conditional_flows()
    demo_loop_flows()
    demo_recorder_simulation()
    
    print("\n" + "#"*60)
    print("# All demos completed!")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()

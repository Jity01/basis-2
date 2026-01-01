"""
Generate large test data file for agent rollouts
Target: ~1 million tokens (~750,000 words)
"""

import json
import random
from datetime import datetime, timedelta

# Agent names and types
AGENT_NAMES = [
    "CustomerSupportAgent",
    "SalesAgent",
    "TechnicalSupportAgent",
    "BillingAgent",
    "OnboardingAgent",
    "RetentionAgent",
    "ProductAgent",
    "ComplianceAgent",
]

# User actions
USER_ACTIONS = [
    "asked about product features",
    "requested a refund",
    "reported a bug",
    "asked for technical help",
    "wanted to upgrade plan",
    "had billing questions",
    "needed account recovery",
    "requested feature documentation",
]

# Agent responses
AGENT_RESPONSES = [
    "I understand your concern. Let me help you with that.",
    "Thank you for reaching out. I can assist you with this issue.",
    "I'll need to gather some information to help you better.",
    "Let me check our system for your account details.",
    "I can definitely help you resolve this. Here's what we can do:",
    "Based on your request, I recommend the following approach:",
    "I've reviewed your case and here's the solution:",
    "Let me escalate this to our specialist team for you.",
]

# System messages
SYSTEM_MESSAGES = [
    "Agent connected to user",
    "Agent retrieved user account information",
    "Agent accessed knowledge base",
    "Agent consulted with supervisor",
    "Agent updated ticket status",
    "Agent generated response",
    "Agent closed conversation",
]


def generate_agent_interaction(agent_name, interaction_id):
    """Generate a single agent interaction"""
    start_time = datetime.now() - timedelta(days=random.randint(0, 30))

    # Generate conversation turns
    turns = []
    num_turns = random.randint(5, 15)

    for i in range(num_turns):
        if i % 2 == 0:  # User turn
            turns.append(
                {
                    "role": "user",
                    "timestamp": (start_time + timedelta(minutes=i * 2)).isoformat(),
                    "action": random.choice(USER_ACTIONS),
                    "message": generate_user_message(),
                }
            )
        else:  # Agent turn
            turns.append(
                {
                    "role": "agent",
                    "timestamp": (
                        start_time + timedelta(minutes=i * 2 + 1)
                    ).isoformat(),
                    "agent_name": agent_name,
                    "response": random.choice(AGENT_RESPONSES),
                    "message": generate_agent_message(),
                    "system_actions": random.sample(
                        SYSTEM_MESSAGES, random.randint(1, 3)
                    ),
                }
            )

    return {
        "interaction_id": f"INT-{interaction_id:06d}",
        "agent_name": agent_name,
        "start_time": start_time.isoformat(),
        "end_time": (start_time + timedelta(minutes=num_turns * 2)).isoformat(),
        "duration_seconds": num_turns * 2 * 60,
        "status": random.choice(["completed", "escalated", "pending", "resolved"]),
        "user_satisfaction": random.choice(
            ["satisfied", "neutral", "dissatisfied", "very_satisfied"]
        ),
        "turns": turns,
        "summary": generate_summary(agent_name, num_turns),
        "metrics": {
            "total_tokens": random.randint(500, 2000),
            "response_time_avg_ms": random.randint(500, 3000),
            "escalations": random.randint(0, 2),
            "knowledge_base_queries": random.randint(0, 5),
        },
    }


def generate_user_message():
    """Generate a realistic user message"""
    templates = [
        "I'm having trouble with {feature}. Can you help me?",
        "I need to {action} but I'm not sure how to do it.",
        "There's an issue with my account - {issue}.",
        "I'd like to know more about {topic}.",
        "Can you explain how {feature} works?",
        "I'm getting an error when I try to {action}.",
        "Is it possible to {request}?",
        "I want to {action} but I don't see the option.",
    ]

    features = [
        "payment processing",
        "data export",
        "user management",
        "API access",
        "reporting",
        "notifications",
    ]
    actions = [
        "upgrade my plan",
        "cancel my subscription",
        "change my email",
        "reset my password",
        "download my data",
    ]
    issues = [
        "I can't log in",
        "my payment failed",
        "I'm missing some features",
        "the interface is slow",
    ]
    topics = [
        "pricing plans",
        "security features",
        "integration options",
        "data retention",
        "compliance",
    ]
    requests = [
        "get a refund",
        "change my billing cycle",
        "add more users",
        "export my data",
    ]

    template = random.choice(templates)
    message = template.format(
        feature=random.choice(features),
        action=random.choice(actions),
        issue=random.choice(issues),
        topic=random.choice(topics),
        request=random.choice(requests),
    )

    # Add some variation
    if random.random() < 0.3:
        message += " " + " ".join(
            [
                f"Additional detail {i+1} about the request."
                for i in range(random.randint(1, 3))
            ]
        )

    return message


def generate_agent_message():
    """Generate a realistic agent response message"""
    templates = [
        "I understand you're experiencing {issue}. Let me help you resolve this.",
        "Thank you for contacting us about {topic}. Here's what I can do:",
        "I've reviewed your account and I can help you with {request}.",
        "Based on your question about {feature}, here's the information:",
        "I can definitely assist you with {action}. The process is as follows:",
    ]

    template = random.choice(templates)
    message = template.format(
        issue=random.choice(["this issue", "a problem", "difficulties"]),
        topic=random.choice(["your account", "this feature", "your request"]),
        request=random.choice(["this", "your request", "what you need"]),
        feature=random.choice(["this feature", "the system", "our platform"]),
        action=random.choice(["this", "your request", "what you're trying to do"]),
    )

    # Add detailed explanation
    explanations = [
        "First, you'll need to navigate to the settings page. Then, look for the section labeled 'Account Management'. In that section, you'll find the option you're looking for.",
        "The system works by processing your request through our automated pipeline. This typically takes 2-3 minutes, but can take up to 10 minutes during peak hours.",
        "To complete this action, you'll need to verify your identity. We'll send a confirmation code to your registered email address. Once you enter that code, the process will complete automatically.",
        "This feature is available in our premium plans. If you're on a basic plan, you can upgrade by going to your account settings and selecting 'Upgrade Plan' from the billing section.",
        "The error you're seeing is typically caused by a temporary system issue. Try refreshing the page or clearing your browser cache. If the problem persists, it may be a known issue that our engineering team is working on.",
    ]

    message += " " + random.choice(explanations)

    # Add closing
    closings = [
        "Please let me know if you need any further assistance.",
        "If you have any other questions, feel free to ask.",
        "I hope this helps! Is there anything else I can assist you with?",
        "Let me know if this resolves your issue or if you need additional help.",
    ]

    message += " " + random.choice(closings)

    return message


def generate_summary(agent_name, num_turns):
    """Generate a summary of the interaction"""
    return f"The {agent_name} handled a customer interaction with {num_turns} conversation turns. The agent addressed the customer's concerns, provided detailed information, and worked to resolve the issue. The interaction involved multiple exchanges where the agent gathered information, consulted knowledge bases, and provided step-by-step guidance to help the customer achieve their goal."


def generate_rollout_data(target_words=750000):
    """Generate agent rollout data targeting approximately target_words"""
    print(f"Generating agent rollout data targeting ~{target_words:,} words...")

    interactions = []
    word_count = 0
    interaction_id = 1

    # Estimate words per interaction (roughly)
    avg_words_per_interaction = 500  # Conservative estimate

    target_interactions = target_words // avg_words_per_interaction

    print(f"Generating approximately {target_interactions:,} interactions...")

    while word_count < target_words * 0.9:  # Stop at 90% to account for JSON structure
        agent_name = random.choice(AGENT_NAMES)
        interaction = generate_agent_interaction(agent_name, interaction_id)

        # Rough word count estimate
        interaction_str = json.dumps(interaction)
        word_count += len(interaction_str.split())

        interactions.append(interaction)
        interaction_id += 1

        if interaction_id % 100 == 0:
            print(
                f"Generated {interaction_id:,} interactions (~{word_count:,} words)..."
            )

    rollout_data = {
        "rollout_id": "ROLLOUT-2024-Q1",
        "description": "Agent rollout test data for performance testing",
        "generated_at": datetime.now().isoformat(),
        "total_interactions": len(interactions),
        "total_words": word_count,
        "agents_involved": list(set(AGENT_NAMES)),
        "date_range": {
            "start": min(i["start_time"] for i in interactions),
            "end": max(i["end_time"] for i in interactions),
        },
        "interactions": interactions,
    }

    return rollout_data


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Rollout Test Data Generator")
    print("=" * 60)

    data = generate_rollout_data(target_words=750000)

    output_file = "agent_rollout_test_data.json"
    print(f"\nWriting data to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size_mb = len(json.dumps(data).encode("utf-8")) / (1024 * 1024)

    print(f"\n✓ Generated {data['total_interactions']:,} interactions")
    print(f"✓ Estimated {data['total_words']:,} words")
    print(f"✓ File size: {file_size_mb:.2f} MB")
    print(f"✓ Saved to: {output_file}")
    print("\n" + "=" * 60)

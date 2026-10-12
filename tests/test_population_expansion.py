"""Unit tests for multi-agent swarm population expansion."""

import pytest
from app.cli import build_parser
from app.services.entity_reader import EntityNode
from app.services.oasis_profile_generator import OasisProfileGenerator


def test_cli_parser_agent_count():
    parser = build_parser()
    args = parser.parse_args(["run", "--files", "test.md", "--requirement", "Predict outcome", "--agent-count", "35"])
    assert args.agent_count == 35


def test_expand_entities_to_population():
    generator = OasisProfileGenerator()
    seed_entities = [
        EntityNode(
            uuid="node-1",
            name="City Transportation Dept",
            labels=["Entity", "GovernmentAgency"],
            summary="Municipal transit authority regulating toll prices.",
            attributes={"type": "official"},
        ),
        EntityNode(
            uuid="node-2",
            name="Commuters",
            labels=["Entity", "Group"],
            summary="Everyday vehicle drivers using expressway corridors.",
            attributes={"type": "group"},
        ),
        EntityNode(
            uuid="node-3",
            name="Delivery Companies",
            labels=["Entity", "Company"],
            summary="Commercial freight and delivery operators.",
            attributes={"type": "commercial"},
        ),
        EntityNode(
            uuid="node-4",
            name="Transit Advocates",
            labels=["Entity", "NGO"],
            summary="Advocates for public transit and clean mobility.",
            attributes={"type": "activist"},
        ),
    ]

    target_count = 20
    expanded = generator.expand_entities_to_population(seed_entities, target_count=target_count)

    assert len(expanded) == target_count
    # Check that uuids are unique
    uuids = [e.uuid for e in expanded]
    assert len(set(uuids)) == target_count

    # Check diverse stances exist
    stances = {e.attributes.get("stance") for e in expanded if e.attributes.get("stance")}
    assert len(stances) >= 3

    # Check demographic variations
    mbtis = {e.attributes.get("mbti") for e in expanded if e.attributes.get("mbti")}
    assert len(mbtis) >= 4


def test_generate_profiles_with_swarm_population():
    generator = OasisProfileGenerator()
    seed_entities = [
        EntityNode(
            uuid="node-commuters",
            name="Commuters",
            labels=["Entity", "Group"],
            summary="Everyday highway drivers.",
            attributes={},
        ),
        EntityNode(
            uuid="node-dept",
            name="City Dept",
            labels=["Entity", "GovernmentAgency"],
            summary="Official road department.",
            attributes={},
        ),
    ]

    profiles = generator.generate_profiles_from_entities(
        entities=seed_entities,
        use_llm=False,
        target_agent_count=12,
    )

    assert len(profiles) == 12
    # Verify user_ids are sequentially assigned 0..11
    user_ids = [p.user_id for p in profiles]
    assert user_ids == list(range(12))

    # Verify all profiles have personas and bios
    for p in profiles:
        assert p.persona
        assert p.bio
        assert p.user_name

"""
tag_maps.py
Static lookup dictionaries mapping user-facing investigation types and evidence
types to the capability_tags that exist in tools.json.

Drives Signal 1 (+3 investigation match) and Signal 4 (+1 evidence match)
in the scoring engine.
"""

INVESTIGATION_TAG_MAP: dict[str, list[str]] = {
    "CSAM detection": [
        "csam_detection", "csam_hash_matching", "csam_scanning",
        "csam_database", "hash_matching", "csam_categorization",
        "csam_reporting",
    ],
    "AI-Generated CSAM": [
        "ai_classification", "deepfake_detection", "ai_analysis",
        "ai_audio_detection", "synthetic_media_analysis", "csam_detection",
    ],
    "Self-Generated CSAM": [
        "csam_detection", "csam_investigation", "victim_identification",
        "image_matching", "content_moderation",
    ],
    "online grooming": [
        "social_media_intelligence", "username_enumeration", "osint",
        "pattern_matching",
    ],
    "crypto tracing": [
        "blockchain_tracing", "crypto_forensics", "bitcoin_analysis",
        "aml_compliance", "token_extraction",
    ],
    "dark web": [
        "dark_web_monitoring", "threat_intelligence", "osint",
        "p2p_monitoring", "bittorrent_monitoring",
    ],
    "trafficking": [
        "victim_identification", "osint", "link_analysis",
        "international_collaboration", "case_management",
    ],
    "sextortion": [
        "social_media_intelligence", "ip_capture", "osint",
        "username_enumeration", "email_harvesting",
    ],
    "cross-border": [
        "international_collaboration", "intelligence_management",
        "case_management", "records_management",
    ],
    "social media investigation": [
        "osint", "social_media_intelligence", "username_enumeration",
        "web_capture", "evidence_preservation",
    ],
    "digital forensics": [
        "digital_forensics", "disk_analysis", "memory_forensics",
        "mobile_forensics", "artifact_recovery",
    ],
    "media authentication": [
        "image_authentication", "tamper_detection", "deepfake_detection",
        "media_forensics", "metadata_extraction", "error_level_analysis",
    ],
    "forensic linguistics": [
        "pattern_matching", "data_extraction", "osint",
        "report_generation",
    ],
    "undercover operations": [
        "ip_capture", "web_capture", "evidence_preservation",
        "p2p_monitoring", "bittorrent_monitoring",
    ],
    "threat intelligence": [
        "threat_intelligence", "dark_web_monitoring",
        "infrastructure_monitoring", "vulnerability_scanning",
        "ioc_scanning",
    ],
}

INPUT_TAG_MAP: dict[str, list[str]] = {
    "Username": [
        "username_enumeration", "osint", "social_media_intelligence",
    ],
    "Email address": [
        "email_harvesting", "osint", "data_extraction",
    ],
    "Phone number": [
        "osint", "data_extraction", "mobile_forensics",
    ],
    "Image / photo": [
        "image_authentication", "csam_detection", "hash_matching",
        "metadata_extraction", "perceptual_hashing", "image_forensics",
    ],
    "Video": [
        "video_enhancement", "media_forensics", "cctv_forensics",
        "deepfake_detection",
    ],
    "Crypto wallet address": [
        "blockchain_tracing", "crypto_forensics", "bitcoin_analysis",
        "aml_compliance",
    ],
    "Domain / IP": [
        "osint", "infrastructure_monitoring", "vulnerability_scanning",
        "iot_search", "web_reconnaissance",
    ],
    "Social media profile": [
        "social_media_intelligence", "osint", "username_enumeration",
        "web_capture",
    ],
    "Hash / fingerprint": [
        "hash_matching", "hash_database", "csam_hash_matching",
        "perceptual_hashing",
    ],
    "Encrypted file": [
        "password_cracking", "data_extraction", "digital_forensics",
    ],
    "Mobile device": [
        "mobile_extraction", "mobile_forensics", "bypassing_locks",
        "android_forensics", "ios_forensics",
    ],
    "Cloud storage": [
        "cloud_extraction", "cloud_forensics", "data_extraction",
    ],
    "Document": [
        "metadata_extraction", "data_extraction", "artifact_extraction",
    ],
    "Chat logs": [
        "data_decoding", "artifact_recovery", "pattern_matching",
        "browser_forensics",
    ],
}


def get_relevant_tags(
    investigation_types: list[str],
    input_types: list[str],
) -> tuple[set[str], set[str]]:
    """
    Expand user selections into two flat sets of relevant capability_tags.

    Returns:
        (investigation_tags, input_tags)
    """
    inv_tags: set[str] = set()
    for inv_type in investigation_types:
        inv_tags.update(INVESTIGATION_TAG_MAP.get(inv_type, []))

    inp_tags: set[str] = set()
    for inp_type in input_types:
        inp_tags.update(INPUT_TAG_MAP.get(inp_type, []))

    return inv_tags, inp_tags

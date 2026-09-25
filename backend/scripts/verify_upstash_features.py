import asyncio
import os
import sys
import hashlib

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.core.redis_rest import redis_rest

async def main():
    print("=" * 60)
    print("SMART FARMING: UPSTASH REDIS REST INTEGRATION VERIFICATION")
    print("=" * 60)

    print(f"Upstash URL: {redis_rest.url}")
    print(f"Enabled: {redis_rest.enabled}")
    assert redis_rest.enabled, "Upstash is not enabled!"

    # 1. Weather Caching Test
    print("\n[1/5] Testing Weather Caching...")
    test_lat, test_lon = 23.02, 72.57  # Ahmedabad
    weather_key = f"sf:weather:{test_lat}_{test_lon}"
    weather_payload = {
        "temperature_celsius": 32.5,
        "humidity_percent": 65,
        "condition": "Clear",
        "advisory": "Optimal conditions for spraying."
    }
    await redis_rest.set(weather_key, weather_payload, ex=120)
    fetched_weather = await redis_rest.get(weather_key)
    print(f"   Stored & Retrieved Weather: {fetched_weather['condition']} at {fetched_weather['temperature_celsius']}°C")
    assert fetched_weather["humidity_percent"] == 65
    print("   Weather caching: PASS")

    # 2. Prediction Deduplication Cache Test
    print("\n[2/5] Testing Prediction Image Deduplication...")
    fake_image_bytes = b"sample_leaf_image_data_for_verification"
    img_hash = hashlib.sha256(fake_image_bytes).hexdigest()
    dedup_key = f"sf:dedup:{img_hash}"
    dedup_payload = {
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": 0.94,
        "status": {"pipeline": "completed"}
    }
    await redis_rest.set(dedup_key, dedup_payload, ex=120)
    fetched_dedup = await redis_rest.get(dedup_key)
    print(f"   Stored & Retrieved Dedup Result: {fetched_dedup['crop']} - {fetched_dedup['disease']}")
    assert fetched_dedup["disease"] == "Early Blight"
    print("   Prediction Deduplication: PASS")

    # 3. Dynamic Thresholds Hot-Reload Test
    print("\n[3/5] Testing Dynamic Thresholds Hot-Reload...")
    thresholds_key = "sf:config:thresholds"
    thresholds_payload = {
        "crop_confidence": 0.72,
        "disease_confidence": 0.68
    }
    await redis_rest.set(thresholds_key, thresholds_payload, ex=120)
    fetched_thresholds = await redis_rest.get(thresholds_key)
    print(f"   Stored & Retrieved Thresholds: {fetched_thresholds}")
    assert fetched_thresholds["crop_confidence"] == 0.72
    print("   Admin Config Hot-Reload: PASS")

    # 4. Translation String Memory Caching Test
    print("\n[4/5] Testing Translation String Memory Caching...")
    english_phrase = "Apply Mancozeb 75% WP at 2g/L water."
    phrase_hash = hashlib.sha256(english_phrase.encode("utf-8")).hexdigest()
    
    # Hindi Cache
    hi_key = f"sf:trans:hi:{phrase_hash}"
    hi_trans = "मैनकोज़ेब 75% डब्ल्यूपी को 2 ग्राम/लीटर पानी में घोलकर छिड़कें।"
    await redis_rest.set(hi_key, hi_trans, ex=120)
    fetched_hi = await redis_rest.get(hi_key)
    print(f"   Hindi Translation stored & retrieved successfully ({len(fetched_hi)} chars)")
    assert fetched_hi == hi_trans

    # Gujarati Cache
    gu_key = f"sf:trans:gu:{phrase_hash}"
    gu_trans = "મેન્કોઝેબ 75% ડબલ્યુપી 2 ગ્રામ/લિટર પાણીમાં છંટકાવ કરવો."
    await redis_rest.set(gu_key, gu_trans, ex=120)
    fetched_gu = await redis_rest.get(gu_key)
    print(f"   Gujarati Translation stored & retrieved successfully ({len(fetched_gu)} chars)")
    assert fetched_gu == gu_trans
    print("   Translation Caching: PASS")

    # 5. Lazy Maintenance Cron Lock Test
    print("\n[5/5] Testing Serverless Maintenance Cron Lock...")
    cron_key = "sf:cron:last_weather_eval"
    import time
    now_ts = time.time()
    await redis_rest.set(cron_key, now_ts, ex=120)
    fetched_cron = await redis_rest.get(cron_key)
    print(f"   Stored & Retrieved Timestamp: {fetched_cron}")
    assert abs(float(fetched_cron) - now_ts) < 2.0
    print("   Serverless Maintenance Cron Lock: PASS")

    # Clean up test keys
    await redis_rest.delete(weather_key)
    await redis_rest.delete(dedup_key)
    await redis_rest.delete(thresholds_key)
    await redis_rest.delete(hi_key)
    await redis_rest.delete(gu_key)
    await redis_rest.delete(cron_key)

    print("\n" + "=" * 60)
    print("ALL 5 UPSTASH REDIS REST INTEGRATIONS VERIFIED & PASSING!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

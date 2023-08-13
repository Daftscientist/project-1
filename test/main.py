import cache
import asyncio

# Path: test\main.py

print(cache.CACHED_DATA)
print(cache.CACHED_EMAIL_TO_UUID)
print("----------------------------------")


print(asyncio.run(cache.get("uuid")))
print("----------------------------------")


print(asyncio.run(cache.update("uuid", session_id="new_session_id")))
print("----------------------------------")


print(asyncio.run(cache.get("uuid")))
print("----------------------------------")

print(cache.CACHED_DATA)
print(cache.CACHED_EMAIL_TO_UUID)
print("----------------------------------")

#!/usr/bin/env python3
"""
Comprehensive test script for PlanaBaseModel operations using GuildPreferences.
This script demonstrates all available operations in the base model.
"""

import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import or_

from plana.database.models.guild import GuildPreferences
from plana.database.utils.db import PlanaDB


class TestBaseOperations:
    """Test class for demonstrating all base model operations."""

    def __init__(self):
        self.test_guild_ids = [
            12345,
            67890,
            11111,
            22222,
            33333,
            44444,
            55555,
            66666,
            77777,
            88888,
            99999,
        ]

    async def setup_database(self):
        """Initialize database connection."""
        print("🔧 Setting up database connection...")
        load_dotenv()
        PlanaDB.init_db(connection_string=os.getenv("DATABASE_URL"))
        print("✅ Database connection established")

    async def cleanup_test_data(self):
        """Clean up test data before and after tests."""
        print("🧹 Cleaning up test data...")
        await GuildPreferences.bulk_delete(GuildPreferences.id.in_(self.test_guild_ids))
        print("✅ Test data cleaned up")

    async def test_core_operations(self):
        """Test core CRUD operations."""
        print("\n" + "=" * 50)
        print("🔍 Testing Core Operations")
        print("=" * 50)

        # Test save()
        print("\n1. Testing save() operation...")
        guild1 = GuildPreferences(
            guild_id=12345,
            enabled=True,
            command_prefix="!",
            language="en-US",
            embed_color="#FF5733",
        )
        await guild1.save()
        print(f"✅ Created guild: {guild1}")

        # Test update()
        print("\n2. Testing update() operation...")
        await guild1.update(
            command_prefix="?", embed_color="#33FF57", embed_footer="Updated footer"
        )
        print(f"✅ Updated guild: {guild1}")

        # Test refresh()
        print("\n3. Testing refresh() operation...")
        await guild1.refresh()
        print(f"✅ Refreshed guild: {guild1}")

        # Test delete() (we'll create another one for this)
        print("\n4. Testing delete() operation...")
        temp_guild = GuildPreferences(guild_id=99999, enabled=False)
        await temp_guild.save()
        result = await temp_guild.delete()
        print(f"✅ Deleted guild: {result}")

    async def test_query_operations(self):
        """Test query operations."""
        print("\n" + "=" * 50)
        print("🔍 Testing Query Operations")
        print("=" * 50)

        # Create test data
        print("\n📝 Creating test data...")
        test_guilds = [
            {
                "guild_id": 67890,
                "enabled": True,
                "command_prefix": "!!",
                "language": "es-ES",
            },
            {
                "guild_id": 11111,
                "enabled": False,
                "command_prefix": ".",
                "language": "fr-FR",
            },
            {
                "guild_id": 22222,
                "enabled": True,
                "command_prefix": "/",
                "language": "de-DE",
            },
            {
                "guild_id": 33333,
                "enabled": True,
                "command_prefix": "!",
                "language": "ja-JP",
            },
        ]

        await GuildPreferences.bulk_create(test_guilds)
        print("✅ Test data created")

        # Test get()
        print("\n1. Testing get() operation...")
        guild = await GuildPreferences.get(12345)
        print(f"✅ Found guild by ID: {guild}")

        # Test get_or_404()
        print("\n2. Testing get_or_404() operation...")
        try:
            guild = await GuildPreferences.get_or_404(12345)
            print(f"✅ Found guild: {guild}")
        except ValueError as e:
            print(f"❌ Error: {e}")

        # Test get_by()
        print("\n3. Testing get_by() operation...")
        guild = await GuildPreferences.get_by(language="es-ES")
        print(f"✅ Found guild by language: {guild}")

        # Test filter()
        print("\n4. Testing filter() operation...")
        enabled_guilds = await GuildPreferences.filter(
            GuildPreferences.enabled == True,
            limit=3,
            order_by=GuildPreferences.id,
        )
        print(f"✅ Found {len(enabled_guilds)} enabled guilds")
        for guild in enabled_guilds:
            print(f"   - {guild}")

        # Test filter() with multiple conditions
        print("\n4b. Testing filter() with multiple conditions...")

        # Example 1: AND conditions - enabled guilds with specific language
        multilang_guilds = await GuildPreferences.filter(
            GuildPreferences.enabled == True,
            GuildPreferences.language.in_(["es-ES", "ja-JP", "de-DE"]),
            order_by=GuildPreferences.id,
        )
        print(
            f"✅ Found {len(multilang_guilds)} enabled guilds with specific languages"
        )
        for guild in multilang_guilds:
            print(f"   - Guild {guild.id}: {guild.language} (enabled: {guild.enabled})")

        # Example 2: Complex conditions - guilds with specific prefixes OR disabled
        complex_guilds = await GuildPreferences.filter(
            or_(
                GuildPreferences.command_prefix.in_(["!!", ".", "/"]),
                GuildPreferences.enabled == False,
            ),
            order_by=GuildPreferences.id,
        )
        print(
            f"✅ Found {len(complex_guilds)} guilds with special prefixes or disabled"
        )
        for guild in complex_guilds:
            print(
                f"   - Guild {guild.id}: prefix='{guild.command_prefix}', enabled={guild.enabled}"
            )

        # Example 3: Range and text conditions
        range_guilds = await GuildPreferences.filter(
            GuildPreferences.id >= 20000,
            GuildPreferences.id <= 70000,
            GuildPreferences.language.like("%-ES"),  # Spanish variants
            order_by=GuildPreferences.id,
        )
        print(
            f"✅ Found {len(range_guilds)} guilds in ID range 20000-70000 with Spanish"
        )
        for guild in range_guilds:
            print(f"   - Guild {guild.id}: {guild.language}")

        # Example 4: NOT conditions
        not_default_guilds = await GuildPreferences.filter(
            GuildPreferences.command_prefix != "!",
            GuildPreferences.language != "en-US",
            GuildPreferences.enabled == True,
            order_by=GuildPreferences.id,
        )
        print(
            f"✅ Found {len(not_default_guilds)} enabled guilds with non-default settings"
        )
        for guild in not_default_guilds:
            print(
                f"   - Guild {guild.id}: prefix='{guild.command_prefix}', lang={guild.language}"
            )

        # Test filter_by()
        print("\n5. Testing filter_by() operation...")
        enabled_guilds = await GuildPreferences.filter_by(
            enabled=True, limit=2, order_by=GuildPreferences.id.desc()
        )
        print(f"✅ Found {len(enabled_guilds)} enabled guilds (filter_by)")
        for guild in enabled_guilds:
            print(f"   - {guild}")

        # Test all()
        print("\n6. Testing all() operation...")
        all_guilds = await GuildPreferences.all(limit=10, order_by=GuildPreferences.id)
        print(f"✅ Found {len(all_guilds)} total guilds")

        # Test first()
        print("\n7. Testing first() operation...")
        first_guild = await GuildPreferences.first(enabled=True)
        print(f"✅ First enabled guild: {first_guild}")

        # Test exists()
        print("\n8. Testing exists() operation...")
        exists = await GuildPreferences.exists(guild_id=12345)
        print(f"✅ Guild 12345 exists: {exists}")

        not_exists = await GuildPreferences.exists(guild_id=99999)
        print(f"✅ Guild 99999 exists: {not_exists}")

    async def test_count_operations(self):
        """Test count operations."""
        print("\n" + "=" * 50)
        print("🔍 Testing Count Operations")
        print("=" * 50)

        # Test count()
        print("\n1. Testing count() operation...")
        total_count = await GuildPreferences.count()
        print(f"✅ Total guilds: {total_count}")

        enabled_count = await GuildPreferences.count(GuildPreferences.enabled == True)
        print(f"✅ Enabled guilds: {enabled_count}")

        # Test count_by()
        print("\n2. Testing count_by() operation...")
        enabled_count = await GuildPreferences.count_by(enabled=True)
        print(f"✅ Enabled guilds (count_by): {enabled_count}")

        prefix_count = await GuildPreferences.count_by(command_prefix="!")
        print(f"✅ Guilds with '!' prefix: {prefix_count}")

    async def test_bulk_operations(self):
        """Test bulk operations."""
        print("\n" + "=" * 50)
        print("🔍 Testing Bulk Operations")
        print("=" * 50)

        # Test bulk_create() - already used above, but let's do another example
        print("\n1. Testing bulk_create() operation...")
        bulk_data = [
            {"guild_id": 44444, "enabled": True, "language": "ko-KR"},
            {"guild_id": 55555, "enabled": False, "language": "zh-CN"},
            {"guild_id": 66666, "enabled": True, "language": "pt-BR"},
        ]

        created = await GuildPreferences.bulk_create(bulk_data)
        print(f"✅ Bulk created {len(created)} guilds")

        # Test bulk_update()
        print("\n2. Testing bulk_update() operation...")
        updates = [
            {"guild_id": 44444, "embed_color": "#FF0000"},
            {"guild_id": 55555, "embed_color": "#00FF00"},
            {"guild_id": 66666, "embed_color": "#0000FF"},
        ]

        updated_count = await GuildPreferences.bulk_update(
            updates, key_field="guild_id"
        )
        print(f"✅ Bulk updated {updated_count} guilds")

        # Test bulk_delete()
        print("\n3. Testing bulk_delete() operation...")
        deleted_count = await GuildPreferences.bulk_delete(
            GuildPreferences.id.in_([44444, 55555, 66666])
        )
        print(f"✅ Bulk deleted {deleted_count} guilds")

    async def test_create_or_update_operations(self):
        """Test create or update operations."""
        print("\n" + "=" * 50)
        print("🔍 Testing Create or Update Operations")
        print("=" * 50)

        # Test get_or_create()
        print("\n1. Testing get_or_create() operation...")

        # First call - should create
        guild1, created = await GuildPreferences.get_or_create(
            guild_id=77777, defaults={"enabled": True, "language": "it-IT"}
        )
        print(f"✅ Get or create result: {guild1}, created: {created}")

        # Second call - should get existing
        guild2, created = await GuildPreferences.get_or_create(
            guild_id=77777, defaults={"enabled": False, "language": "ru-RU"}
        )
        print(f"✅ Get or create result: {guild2}, created: {created}")

        # Test update_or_create()
        print("\n2. Testing update_or_create() operation...")

        # Update existing
        guild3, created = await GuildPreferences.update_or_create(
            guild_id=77777, defaults={"embed_color": "#PURPLE", "command_prefix": ">>"}
        )
        print(f"✅ Update or create result: {guild3}, created: {created}")

        # Create new
        guild4, created = await GuildPreferences.update_or_create(
            guild_id=88888, defaults={"enabled": True, "language": "ar-SA"}
        )
        print(f"✅ Update or create result: {guild4}, created: {created}")

    async def test_utility_methods(self):
        """Test utility methods."""
        print("\n" + "=" * 50)
        print("🔍 Testing Utility Methods")
        print("=" * 50)

        # Get a test guild
        guild = await GuildPreferences.get(12345)

        # Test to_dict()
        print("\n1. Testing to_dict() operation...")
        guild_dict = guild.to_dict()
        print(f"✅ Guild as dict: {guild_dict}")

        # Test to_dict() with exclusions
        guild_dict_partial = guild.to_dict(exclude=["embed_footer_images", "timezone"])
        print(f"✅ Guild as dict (partial): {guild_dict_partial}")

        # Test __repr__()
        print("\n2. Testing __repr__() operation...")
        print(f"✅ Guild representation: {repr(guild)}")

    async def run_all_tests(self):
        """Run all tests in sequence."""
        try:
            await self.setup_database()
            await self.cleanup_test_data()

            await self.test_core_operations()
            await self.test_query_operations()
            await self.test_count_operations()
            await self.test_bulk_operations()
            await self.test_create_or_update_operations()
            await self.test_utility_methods()

            print("\n" + "=" * 50)
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 50)

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            raise
        finally:
            await self.cleanup_test_data()


async def main():
    """Main function to run all tests."""
    print("🚀 Starting PlanaBaseModel Operations Test")
    print("=" * 50)

    tester = TestBaseOperations()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

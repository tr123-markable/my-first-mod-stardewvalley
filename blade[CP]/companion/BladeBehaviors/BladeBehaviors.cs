using System;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using StardewValley.Locations;
using StardewValley.Objects;

namespace BladeBehaviors
{
    public class ModEntry : Mod
    {
        private const string NpcName = "blade";
        private const string LastCookKey = "tr.blade.lastCookDay";
        private const string LastGiftKey = "tr.blade.lastGiftWeek";
        private DateTime lastSocialGreeting = DateTime.MinValue;
        private Vector2 lastBladePosition;
        private int bladeStuckSeconds;

        public override void Entry(IModHelper helper)
        {
            helper.Events.Input.ButtonPressed += this.OnButtonPressed;
            helper.Events.GameLoop.OneSecondUpdateTicked += this.OnOneSecondUpdateTicked;
            helper.Events.GameLoop.SaveLoaded += this.OnSaveLoaded;
            helper.Events.GameLoop.DayStarted += this.OnDayStarted;
        }

        private void OnButtonPressed(object sender, ButtonPressedEventArgs e)
        {
            if (!Context.IsWorldReady || Game1.activeClickableMenu != null || !e.Button.IsActionButton())
                return;

            NPC blade = this.FindBladeInFront();
            if (blade == null || blade.currentLocation != Game1.currentLocation)
                return;

            bool inFarmHouse = Game1.currentLocation is FarmHouse;
            bool gaveGift = this.TryGiveWeeklyGift();
            bool cooked = false;
            string dialogue = null;

            if (inFarmHouse && Game1.isRaining)
            {
                string cookResult = this.TryCookFromFridge();
                if (cookResult != null)
                {
                    cooked = true;
                    dialogue = cookResult;
                }
            }

            if (gaveGift)
            {
                this.GiveItem("(O)64", 1, "gift");
                if (dialogue == null)
                    dialogue = "……这个给你。$1";
                else
                    dialogue += "#$b#……这个也给你。$1";
            }

            if (dialogue == null)
                return;

            this.Helper.Input.Suppress(e.Button);
            Game1.DrawDialogue(new Dialogue(blade, null, dialogue));
            this.Monitor.Log(
                $"Blade interaction: cooked={cooked}, gift={gaveGift}",
                LogLevel.Trace
            );
        }

        private NPC FindBladeInFront()
        {
            Vector2 playerTile = Game1.player.Tile;
            Vector2 target;
            switch (Game1.player.FacingDirection)
            {
                case 0:
                    target = playerTile + new Vector2(0, -1);
                    break;
                case 1:
                    target = playerTile + new Vector2(1, 0);
                    break;
                case 2:
                    target = playerTile + new Vector2(0, 1);
                    break;
                default:
                    target = playerTile + new Vector2(-1, 0);
                    break;
            }

            return Game1.currentLocation.characters.FirstOrDefault(
                npc => npc.Name == NpcName && npc.Tile == target
            );
        }

        private string TryCookFromFridge()
        {
            FarmHouse house = Game1.currentLocation as FarmHouse;
            Chest fridge = house?.GetFridge(true);
            if (fridge == null || fridge.Items == null)
                return "……这里没有可以用的冰箱。$3";

            int today = Game1.Date.TotalDays;
            if (Game1.player.modData.TryGetValue(LastCookKey, out string lastCook)
                && lastCook == today.ToString())
            {
                return null;
            }

            int consumed = 0;
            for (int i = 0; i < fridge.Items.Count && consumed < 2; i++)
            {
                Item item = fridge.Items[i];
                if (item == null || item.Stack <= 0 || !(item is StardewValley.Object obj) || obj.Edibility <= 0)
                    continue;

                item.Stack--;
                if (item.Stack <= 0)
                    fridge.Items[i] = null;
                consumed++;
            }

            if (consumed < 2)
                return "……冰箱里的食材不够。$3";

            Game1.player.modData[LastCookKey] = today.ToString();
            Item dish = ItemRegistry.Create("(O)200", 1, 0, true)
                ?? ItemRegistry.Create("(O)194", 1, 0, true);
            if (dish != null)
                Game1.player.addItemByMenuIfNecessary(dish);

            return "……用你冰箱里的东西做的。$1#$b#尝尝。";
        }

        private bool TryGiveWeeklyGift()
        {
            if (!Game1.player.friendshipData.TryGetValue(NpcName, out Friendship friendship)
                || friendship.Points < 2000)
            {
                return false;
            }

            int week = Game1.Date.TotalDays / 7;
            if (Game1.player.modData.TryGetValue(LastGiftKey, out string lastGift)
                && lastGift == week.ToString())
            {
                return false;
            }

            Game1.player.modData[LastGiftKey] = week.ToString();
            return true;
        }

        private void OnOneSecondUpdateTicked(object sender, OneSecondUpdateTickedEventArgs e)
        {
            if (!Context.IsWorldReady || Game1.activeClickableMenu != null || Game1.currentLocation == null)
                return;

            this.ConfigureBladeSafety();

            NPC blade = Game1.getCharacterFromName(NpcName);
            if (blade != null && blade.currentLocation is FarmHouse)
            {
                if (blade.controller != null)
                {
                    if (blade.Position == this.lastBladePosition)
                        this.bladeStuckSeconds++;
                    else
                        this.bladeStuckSeconds = 0;

                    this.lastBladePosition = blade.Position;
                    if (this.bladeStuckSeconds >= 15)
                    {
                        this.Monitor.Log("Blade was stuck in the farmhouse; returning him to the safe hall tile.", LogLevel.Warn);
                        blade.controller = null;
                        blade.Position = new Vector2(27 * Game1.tileSize, 25 * Game1.tileSize);
                        this.bladeStuckSeconds = 0;
                    }
                }
                else
                {
                    this.bladeStuckSeconds = 0;
                    this.lastBladePosition = blade.Position;
                }
            }

            if ((DateTime.UtcNow - this.lastSocialGreeting).TotalSeconds < 60)
                return;

            blade = Game1.currentLocation.characters.FirstOrDefault(npc => npc.Name == NpcName);
            if (blade == null || Vector2.Distance(blade.Tile, Game1.player.Tile) > 12f)
                return;

            NPC nearbyNpc = Game1.currentLocation.characters.FirstOrDefault(
                npc => npc != blade
                    && npc.Name != NpcName
                    && Vector2.Distance(npc.Tile, blade.Tile) <= 2.5f
            );
            if (nearbyNpc == null || Game1.random.NextDouble() > 0.1)
                return;

            this.lastSocialGreeting = DateTime.UtcNow;
            string[] greetings = { "……", "嗯。", "……早。", "有事？" };
            blade.showTextAboveHead(greetings[Game1.random.Next(greetings.Length)]);
        }

        private void OnSaveLoaded(object sender, SaveLoadedEventArgs e)
        {
            this.ConfigureBladeSafety();
        }

        private void OnDayStarted(object sender, DayStartedEventArgs e)
        {
            this.ConfigureBladeSafety();
        }

        private void ConfigureBladeSafety()
        {
            NPC blade = Game1.getCharacterFromName(NpcName);
            if (blade == null)
                return;

            blade.willDestroyObjectsUnderfoot = false;
        }

        private void GiveItem(string itemId, int amount, string purpose)
        {
            Item item = ItemRegistry.Create(itemId, amount, 0, true);
            if (item == null)
            {
                this.Monitor.Log($"Failed to create item {itemId} for {purpose}.", LogLevel.Warn);
                return;
            }

            Game1.player.addItemByMenuIfNecessary(item);
        }
    }
}

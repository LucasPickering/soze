package casecontrol.command;

import casecontrol.command.caseled.*;
import casecontrol.command.general.CommandExit;
import casecontrol.command.general.CommandHelp;
import casecontrol.command.lcd.CommandLcdColor;
import casecontrol.command.lcd.CommandLcdMode;

public enum EnumCommand {

  EXIT(CommandExit.class), HELP(CommandHelp.class),

  CASE_MODE(CommandCaseMode.class), STATIC_COLOR(CommandStaticColor.class),
  SET_FADE_TICKS(CommandSetFadeTicks.class), SET_PAUSE_TICKS(CommandSetPauseTicks.class),
  ADD_FADE_COLOR(CommandAddFadeColor.class), REMOVE_FADE_COLOR(CommandRemoveFadeColor.class),
  FADE_LIST(CommandFadeList.class), CLEAR_FADE(CommandClearFade.class),
  SAVE_FADE_SET(CommandSaveFadeSet.class), LOAD_FADE_SET(CommandLoadFadeSet.class),
  REMOVE_FADE_SET(CommandRemoveFadeSet.class), LIST_FADE_SET(CommandListFadeSet.class),

  LCD_MODE(CommandLcdMode.class), LCD_COLOR(CommandLcdColor.class);

  public final Command command;

  EnumCommand(Class<? extends Command> commandClass) {
    Command command = null;
    try {
      command = commandClass.newInstance();
    } catch (IllegalAccessException | InstantiationException e) {
      e.printStackTrace();
    }
    this.command = command;
  }
}

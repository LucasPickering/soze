package me.lucaspickering.casecontrol.command;

import me.lucaspickering.casecontrol.command.caseled.CommandAddFadeColor;
import me.lucaspickering.casecontrol.command.caseled.CommandCaseMode;
import me.lucaspickering.casecontrol.command.caseled.CommandClearFade;
import me.lucaspickering.casecontrol.command.caseled.CommandFadeList;
import me.lucaspickering.casecontrol.command.caseled.CommandListFadeSet;
import me.lucaspickering.casecontrol.command.caseled.CommandLoadFadeSet;
import me.lucaspickering.casecontrol.command.caseled.CommandRemoveFadeColor;
import me.lucaspickering.casecontrol.command.caseled.CommandRemoveFadeSet;
import me.lucaspickering.casecontrol.command.caseled.CommandSaveFadeSet;
import me.lucaspickering.casecontrol.command.caseled.CommandSetFadeTicks;
import me.lucaspickering.casecontrol.command.caseled.CommandSetPauseTicks;
import me.lucaspickering.casecontrol.command.general.CommandExit;
import me.lucaspickering.casecontrol.command.general.CommandHelp;
import me.lucaspickering.casecontrol.command.general.CommandInfo;
import me.lucaspickering.casecontrol.command.lcd.CommandLcdColor;
import me.lucaspickering.casecontrol.command.lcd.CommandLcdMode;

public enum EnumCommand {

  EXIT(CommandExit.class), HELP(CommandHelp.class), INFO(CommandInfo.class),

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

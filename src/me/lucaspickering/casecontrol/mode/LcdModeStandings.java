package me.lucaspickering.casecontrol.mode;

import java.util.regex.Pattern;

public class LcdModeStandings extends AbstractLcdMode {

    private static String STANDINGS_URL = "http://www.espn.com/nhl/standings";
    private static Pattern STANDINGS_RGX = Pattern.compile("<table.*</table>", Pattern.DOTALL);

    @Override
    public String[] getText() {
        return text;
    }
}

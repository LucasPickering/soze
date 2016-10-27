package me.lucaspickering.casecontrol.mode.lcd;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.Arrays;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import me.lucaspickering.casecontrol.Consts;

public final class LcdModeNhl extends AbstractLcdMode {

    private enum Division {
        ATLANTIC("Atlantic", "atl"),
        METROPOLITAN("Metropolitan", "metro"),
        CENTRAL("Central", "ctl"),
        PACIFIC("Pacific", "pac");

        private final String name;
        private final List<String> abbrevs;

        Division(String name, String... abbrevs) {
            this.name = name;
            this.abbrevs = Arrays.asList(abbrevs);
        }

        @Override
        public String toString() {
            return name;
        }

        private static Division fromString(String name) {
            for (Division div : values()) {
                if (name.equalsIgnoreCase(div.name) || div.abbrevs.contains(name)) {
                    return div;
                }
            }
            return null;
        }
    }

    private enum Team {
        FLORIDA(Division.ATLANTIC, "Florida", "FLA"),
        MONTREAL(Division.ATLANTIC, "Montreal", "MTL"),
        TORONTO(Division.ATLANTIC, "Toronto", "TOR"),
        TAMPA(Division.ATLANTIC, "Tampa Bay", "TBL"),
        OTTAWA(Division.ATLANTIC, "Ottawa", "OTT"),
        BOSTON(Division.ATLANTIC, "Boston", "BOS"),
        BUFFALO(Division.ATLANTIC, "Buffalo", "BUF"),
        DETROIT(Division.ATLANTIC, "Detroit", "DET"),

        PITTSBURGH(Division.METROPOLITAN, "Pittsburgh", "PIT"),
        PHILADELPHIA(Division.METROPOLITAN, "Philadelphia", "PHI"),
        WASHINGTON(Division.METROPOLITAN, "Washington", "WSH"),
        NYRANGERS(Division.METROPOLITAN, "NY Rangers", "NYR"),
        CAROLINA(Division.METROPOLITAN, "Carolina", "CAR"),
        NEWJERSEY(Division.METROPOLITAN, "New Jersey", "NJD"),
        NYISLANDERS(Division.METROPOLITAN, "NY Islanders", "NYI"),
        COLUMBUS(Division.METROPOLITAN, "Columbus", "CBJ"),

        STLOUIS(Division.CENTRAL, "St. Louis", "STL"),
        COLORADO(Division.CENTRAL, "Colorado", "COL"),
        DALLAS(Division.CENTRAL, "Dallas", "DAL"),
        WINNIPEG(Division.CENTRAL, "Winnipeg", "WPG"),
        MINNESOTA(Division.CENTRAL, "Minnesota", "MIN"),
        NASHVILLE(Division.CENTRAL, "Nashville", "NSH"),
        CHICAGO(Division.CENTRAL, "Chicago", "CHI"),

        EDMONTON(Division.PACIFIC, "Edmonton", "EDM"),
        SANJOSE(Division.PACIFIC, "San Jose", "SJS"),
        ARIZONA(Division.PACIFIC, "Arizona", "ARI"),
        VANCOUVER(Division.PACIFIC, "Vancouver", "VAN"),
        CALGARY(Division.PACIFIC, "Calgary", "CGY"),
        ANAHEIM(Division.PACIFIC, "Anaheim", "ANA"),
        LOGANGELES(Division.PACIFIC, "Los Angeles", "LAK");

        private final Division division;
        private final String espnName;
        private final String abbrev;

        Team(Division division, String espnName, String abbrev) {
            this.division = division;
            this.espnName = espnName;
            this.abbrev = abbrev;
        }
    }

    /**
     * A class representing a team's current standings stats. Compare to itself for the purposes
     * of sorting teams by standings location.
     */
    private class Stats implements Comparable<Stats> {

        private final int gamesPlayed;
        private final int wins;
        private final int losses;
        private final int otLosses;
        private final int points;
        private final int roWins;
        private final int soWins;
        private final int soLosses;

        private Stats(int gamesPlayed, int wins, int losses, int otLosses, int points, int roWins,
                      int soWins, int soLosses) {
            this.gamesPlayed = gamesPlayed;
            this.wins = wins;
            this.losses = losses;
            this.otLosses = otLosses;
            this.points = points;
            this.roWins = roWins;
            this.soWins = soWins;
            this.soLosses = soLosses;
        }

        @Override
        public int compareTo(Stats other) {
            int comp;
            // First compare by points
            if ((comp = Integer.compare(points, other.points)) != 0) {
                return comp;
            }

            // Then compare by games played
            if ((comp = Integer.compare(gamesPlayed, other.gamesPlayed)) != 0) {
                return comp;
            }

            // Then compare by ROW
            if ((comp = Integer.compare(roWins, other.roWins)) != 0) {
                return comp;
            }

            return 0; // These teams are the same
        }
    }

    private static final String STANDINGS_URL = "http://www.espn.com/nhl/standings";
    private static final Pattern TABLE_RGX = Pattern.compile("<table.*</table>");
    private static final String TEAM_RGX_FORMAT =
        "%s.*?(?<gp>\\d+).*?(?<w>\\d+).*?(?<l>\\d+).*?(?<otl>\\d+).*?(?<pts>\\d+).*?(?<roWins>\\d+)"
        + ".*?(?<soWins>\\d+).*?(?<soLosses>\\d+)";
    private static final String OUTPUT_FORMAT = "%d. %s %3$-4d";
    private static final Division DEFAULT_DIVISION = Division.METROPOLITAN;

    private Division division = DEFAULT_DIVISION;

    public LcdModeNhl() {
        super(EnumLcdMode.NHL);
    }

    @Override
    public void init(String... args) {
        if (args.length >= 1) {
            // If a division was passed in, use that one. Otherwise the default stays
            final Division div = Division.fromString(args[0]);
            if (div != null) {
                division = div;
            } else {
                System.out.printf("Unknown division '%s', defaulting to '%s'\n",
                                  args[0], division);
            }
        }
    }

    @Override
    public String[] getText() {
        // Standings are re-downloaded and parsed every iteration, because this only gets called
        // every 10 minutes.
        final Map<Team, Stats> standings = getStandings();
        final List<Team> sortedDivision = sortedDivisionStandings(standings, division);
        int i = 0;
        // Use foreach because List access isn't necessarily constant time
        final String[] text = new String[Consts.LCD_HEIGHT];
        for (Team team : sortedDivision) {
            if (i < text.length) {
                text[i] = ""; // If this is the first string to go in the row, clear the row first
            }
            text[i % text.length] += String.format(OUTPUT_FORMAT, i + 1, team.abbrev,
                                                   standings.get(team).points);
            i++;
        }
        return text;
    }

    private Map<Team, Stats> getStandings() {
        final String data = downloadStandings();
        Objects.requireNonNull(data);
        Matcher matcher = TABLE_RGX.matcher(data); // Isolate the standings table data

        // Try to match and check that there was a successful match
        if (!matcher.find()) {
            throw new IllegalStateException("Could not parse standings data!");
        }

        // Match data for each team, and populate the stats map
        final String tableData = matcher.group();
        final Map<Team, Stats> rv = new EnumMap<>(Team.class);
        for (Team team : Team.values()) {
            rv.put(team, getTeamStats(tableData, team));
        }
        return rv;
    }

    /**
     * Downloads the HTML data for the standings page. The output data will NOT contain newline
     * characters.
     *
     * @return the HTML data, or {@code null} if an error occurred
     */
    private String downloadStandings() {
        InputStream is = null;
        try {
            URL url = new URL(STANDINGS_URL);
            is = url.openStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(is));

            // Read everything out of the reader and it put in in a string
            String line;
            StringBuilder builder = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
            return builder.toString();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (is != null) {
                try {
                    is.close();
                } catch (IOException e) {
                    // Who cares
                }
            }
        }
        return null;
    }

    private Stats getTeamStats(String data, Team team) {
        final Pattern teamRgx = Pattern.compile(String.format(TEAM_RGX_FORMAT, team.espnName));
        final Matcher matcher = teamRgx.matcher(data);

        // Try to match and check that there was a successful match
        if (!matcher.find()) {
            throw new IllegalStateException("Could not parse data for: " + team);
        }

        // Get all the stats from the match and build a Stats object
        final int gp = Integer.parseInt(matcher.group("gp"));
        final int w = Integer.parseInt(matcher.group("w"));
        final int l = Integer.parseInt(matcher.group("l"));
        final int otl = Integer.parseInt(matcher.group("otl"));
        final int pts = Integer.parseInt(matcher.group("pts"));
        final int row = Integer.parseInt(matcher.group("roWins"));
        final int sow = Integer.parseInt(matcher.group("soWins"));
        final int sol = Integer.parseInt(matcher.group("soLosses"));
        return new Stats(gp, w, l, otl, pts, row, sow, sol);
    }

    private List<Team> sortedDivisionStandings(Map<Team, Stats> standings, Division division) {
        // Get a list of all teams in this division, sorted ascendingly by Stats.compareTo
        return standings.entrySet().stream().filter(e -> e.getKey().division == division)
            .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue())).map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}

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

public final class LcdModeStandings extends AbstractLcdMode {

    private enum Division {
        ATLANTIC, METROPOLITAN, CENTRAL, PACIFIC
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

    private static final String STANDINGS_URL = "http://www.espn.com/nhl/standings";
    private static final Pattern TABLE_RGX = Pattern.compile("<table.*</table>");

    // Group ordering: GP, W, L, OTL, PTS, ROW, SOW, SOL
    private static final String TEAM_RGX_FORMAT =
        "%s.*?(?<gp>\\d+).*?(?<w>\\d+).*?(?<l>\\d+).*?(?<otl>\\d+).*?(?<pts>\\d+).*?(?<roWins>\\d+)"
        + ".*?(?<soWins>\\d+).*?(?<soLosses>\\d+)";
    private static final String OUTPUT_FORMAT = "%s (%d)";

    private transient final Map<Team, Stats> allStats = new EnumMap<>(Team.class);

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

    public LcdModeStandings() {
        super();
        updateStandings();
    }

    @Override
    public EnumLcdMode getMode() {
        return EnumLcdMode.NHL;
    }

    @Override
    public String[] getText() {
        final List<Team> sortedTeams = sortedDivisionStandings(Division.METROPOLITAN);
        int i = 0;
        Arrays.fill(text, "");
        for (Team team : sortedTeams) {
            text[i] += String.format(OUTPUT_FORMAT, team.abbrev, allStats.get(team).points);
        }
        return text;
    }

    private void updateStandings() {
        final String data = downloadStandings();
        Objects.requireNonNull(data);
        Matcher matcher = TABLE_RGX.matcher(data); // Isolate the standings table data

        // Try to match and check that there was a successful match
        if (!matcher.find()) {
            throw new IllegalStateException("Could not parse standings data!");
        }

        // Match data for each team, and populate the stats map
        final String tableData = matcher.group();
        for (Team team : Team.values()) {
            allStats.put(team, getTeamStats(tableData, team));
        }
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

    private List<Team> sortedDivisionStandings(Division division) {
        // Get a list of all teams in this division, sorted ascendingly by Stats.compareTo
        return allStats.entrySet().stream().filter(e -> e.getKey().division == division)
            .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue())).map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}

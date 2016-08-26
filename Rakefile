require 'pathname'
DATA_DIR = Pathname 'data'
WRANGLE_DIR = Pathname 'wrangle'
CORRAL_DIR = WRANGLE_DIR.join('corral')
SCRIPTS_DIR = WRANGLE_DIR.join('scripts')
DIRS = {
    :fetched => CORRAL_DIR.join('fetched'),
    :converted => CORRAL_DIR.join('converted'),
    :published => DATA_DIR,
}

F_FILES = Hash[{
    '2004' => '2004.shp',
    '2008' => '2008.shp',
    '2012' => '2012.shp',
}.map{|k, v| [k, DIRS[:fetched] / v]}]

C_FILES = Hash[{
    '2004' => '2004.csv',
    '2008' => '2008.csv',
    '2012' => '2012.csv',
    'fips' => 'fips.csv',
}.map{|k, v| [k, DIRS[:converted] / v]}]

P_FILES = Hash[{
    '2004_2012' => 'us-presidential-election-county-results-2004-through-2012.csv',
    '2004_2012_with_wkt' => 'us-presidential-election-county-results-2004-through-2012-with-wkt.csv',
}.map{|k, v| [k, DIRS[:published] / v] }]


desc 'Setup the directories'
task :setup do
    DIRS.each_value do |p|
        p.mkpath()
        puts "Created directory: #{p}"
    end
end


desc "Election results for 2004, 2008, 2012, without WKT data"
file P_FILES['2004_2012'] => C_FILES.values() do
    sh ['python',
        SCRIPTS_DIR / 'collate.py',
        '--omit-wkt',
        '2004', C_FILES['2004'], C_FILES['fips'],
        '>', P_FILES['2004_2012']
    ].join(' ')
    sh ['python',
        SCRIPTS_DIR / 'collate.py',
        '--omit-wkt',
        '2008', C_FILES['2008'], C_FILES['fips'],
        '|', "sed 1d", # skip headers
        '>>', P_FILES['2004_2012']
    ].join(' ')
    sh ['python',
        SCRIPTS_DIR / 'collate.py',
        '--omit-wkt',
        '2012', C_FILES['2012'], C_FILES['fips'],
        '|', "sed 1d", # skip headers
        '>>', P_FILES['2004_2012']
    ].join(' ')
end


# desc "Election results for 2004, 2008, 2012, with WKT data"
# file P_FILES['2004_2012_with_wkt'] => C_FILES.values() do
#     sh ['python',
#         SCRIPTS_DIR / 'collate.py',
#         '2004', C_FILES['2004'], C_FILES['fips'],
#         '>', P_FILES['2004_2012_with_wkt']
#     ].join(' ')
#     sh ['python',
#         SCRIPTS_DIR / 'collate.py',
#         '2008', C_FILES['2008'], C_FILES['fips'],
#         '|', "sed 1d", # skip headers
#         '>>', P_FILES['2004_2012_with_wkt']
#     ].join(' ')
#     sh ['python',
#         SCRIPTS_DIR / 'collate.py',
#         '2012', C_FILES['2012'], C_FILES['fips'],
#         '|', "sed 1d", # skip headers
#         '>>', P_FILES['2004_2012_with_wkt']
#     ].join(' ')
# end


desc "Extract a canonical listing of FIPS and readable fips names"
file C_FILES['fips'] => C_FILES['2008'] do
    sh ['python', SCRIPTS_DIR / 'extract_fips.py',
        C_FILES['2008'], '>', C_FILES['fips']].join(' ')
end

C_FILES.each_pair do |year, fname|
    if year[/\d{4}/]
        desc "Convert .shp to .csv"
        # ogr2ogr -f CSV 2004.csv 2004.shp -lco GEOMETRY=AS_WKT

        file fname => F_FILES[year] do
            sh ['ogr2ogr', '-f', 'CSV',
                fname, F_FILES[year],
                '-lco GEOMETRY=AS_WKT'
               ].join(' ')
        end
    end
end





F_FILES.each_pair do |year, fname|
    desc "Fetch data for #{year}"
    file fname do
        sh ['python', SCRIPTS_DIR + 'fetch_data.py',
        year, DIRS[:fetched]].join(' ')
    end
end

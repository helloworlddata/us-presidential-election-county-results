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
    '2004': '2004.shp',
    '2008': '2008.shp',
    '2012': '2012.shp',
}.map{|k, v| [k, DIRS[:fetched] / v]}]

C_FILES = Hash[{
    '2004': '2004.csv',
    '2008': '2008.csv',
    '2012': '2012.csv',
}.map{|k, v| [k, DIRS[:converted] / v]}]



desc 'Setup the directories'
task :setup do
    DIRS.each_value do |p|
        p.mkpath()
        puts "Created directory: #{p}"
    end
end




C_FILES.each_pair do |year, fname|
    desc "Convert .shp to .csv"
    # ogr2ogr -f CSV 2004.csv 2004.shp -lco GEOMETRY=AS_WKT

    file fname => F_FILES[year] do
        sh ['ogr2ogr', '-f', 'CSV',
            fname, F_FILES[year],
            ].join(' ')
    end
end



F_FILES.each_pair do |year, fname|
    desc "Fetch data for #{year}"
    file fname do
        sh ['python', SCRIPTS_DIR + 'fetch_data.py',
        year, DIRS[:fetched]].join(' ')
    end
end

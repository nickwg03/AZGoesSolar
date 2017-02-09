from AZGS_Scrape_script import *

##----------------------------------------------------------------##

#phantomjs_executable = "/Users/ngrue/Documents/other/phantomjs-2.1.1-macosx/bin/phantomjs"  # PhantomJS needed for headless operation
phantomjs_executable = "./chromedriver"
text_file_output = "./data/"  # directory for text files to go into. Expects additional folders in this directory relating to the program abbreviation in the list below ("aic","aps","dvec", etc...)
final_csv = "./az_goes_extracted_tts10.csv"  # final CSV file



# list of lists below is structured as: incentive program front page, ID of next button (different for each program), name of folder to write extract files into.
# as new programs are installed, this list will need to be updated.
# to find "ID of next button," need to look through page source code and need to manually find "next button" ID.
# for programs without a next button (fewer than 25 records available for program) a next button will not be available. Use None instead.
# if script fails during run, can comment out programs that completed successfully to start up with program script previously failed on.
# will likely need to re-run incentive program from the start should script fail as I don't see a way to start scraping mid-program.
url_info = [
            ['http://arizonagoessolar.org/UtilityIncentives/AjoImprovementCompany.aspx',None,'aic', "Ajo Improvement"],
            ['http://arizonagoessolar.org/UtilityIncentives/ArizonaPublicService.aspx','dnn_ctr421_XModPro_ctl00_ctl01_pgrBottom_lnkNext','aps', "Arizona Public"],
            ['http://arizonagoessolar.org/UtilityIncentives/DuncanValleyElectricCooperative.aspx',None,'dvec', "Duncan Valley"],
            #['http://arizonagoessolar.org/UtilityIncentives/GrahamCountyElectricCooperative.aspx','dnn_ctr431_XModPro_ctl00_ctl01_pgrBottom_lnkNext','gcec', ""],
            ['http://arizonagoessolar.org/UtilityIncentives/MohaveElectricCooperative.aspx','dnn_ctr435_XModPro_ctl00_ctl01_pgrBottom_lnkNext','mec', "Mohave Electric"],
            ['http://arizonagoessolar.org/UtilityIncentives/MorenciWaterandElectric.aspx',None,'mwe', "Morenci"],
            ['http://arizonagoessolar.org/UtilityIncentives/NavopacheElectricCooperative.aspx','dnn_ctr442_XModPro_ctl00_ctl01_pgrBottom_lnkNext','nec', "Navopache"],
            ['http://arizonagoessolar.org/UtilityIncentives/SaltRiverProject.aspx','dnn_ctr446_XModPro_ctl00_ctl01_pgrBottom_lnkNext','srp', "Salt River"],
            ['http://arizonagoessolar.org/UtilityIncentives/SulphurSpringsValleyElectricCooperative.aspx','dnn_ctr450_XModPro_ctl00_ctl01_pgrBottom_lnkNext','ssvec', "Sulpher Springs"],
            ['http://arizonagoessolar.org/UtilityIncentives/TricoElectricCooperative.aspx','dnn_ctr454_XModPro_ctl00_ctl01_pgrBottom_lnkNext','tec', "Trico Electric"],
            ['http://arizonagoessolar.org/UtilityIncentives/TucsonElectricPower.aspx','dnn_ctr458_XModPro_ctl00_ctl01_pgrBottom_lnkNext','tep', "Tucson Electric"],
            ['http://arizonagoessolar.org/UtilityIncentives/UniSourceEnergyServices.aspx','dnn_ctr462_XModPro_ctl00_ctl01_pgrBottom_lnkNext','ues', "UniSource Energy"]
            ]

scraper = AZScrape(phantomjs_executable, text_file_output, final_csv)

# STEP 1 - scrape website, writing text files for each page
for item in url_info:
    scraper.extract(item)


# STEP 2 - scan through each program folder and remove duplicates.
#for item in url_info:
#    scraper.cleanFiles(item)


# OPTIONAL STEP - list all "additional fields" (fields located in dropdown of rows on program site)
#attributes_l = []
#for item in url_info:
#    result = scraper.checkadditionalattributes(item, attributes_l)
#    attributes_l.extend(result)
#for item in attributes_l:
#    print item


# STEP 3 - consolidate all individual text files into single CSV
#self.consolidate(url_info)

print("Done")

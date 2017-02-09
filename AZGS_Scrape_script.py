import contextlib, time, sys, glob, os, csv
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lxml.html as LH
import lxml.html.clean as clean
import collections
import traceback


class AZScrape(object):
    def __init__(self, webdriver_path, text_file_output, final_csv):
        self.webdriver_path = webdriver_path
        self.text_file_output = text_file_output
        self.final_csv = final_csv


    def extract(self, incoming):
        """
        The script below opens the AZGoesSolar website and navigates through each incentive program, download the contents of the page and clicking the "next" button.
        The script is a little finicky in that it won't necessarily get a 1-to-1 extraction of each page, instead it will periodically extract a page that has
        previously been extracted, causing duplicate extraction files.
        The including function cleanFiles() will go through all of the files for each incentive program and delete duplicates.

        Be advised! Script may fail inexplicably while scraping (seems to be weakness of scraping in general using Selenium). If script stops mid-incentive program, will need to re-run program to collect all pages.
        You can get an idea if script completed or failed by checking the last resultsXX.txt file and searching for section that looks like this: "Page 792 of 792".
        If last text file indicates that page number hadn't reached the last page, script failed before finishing and will need to be rerun.
        """
        url, nextlink, directory, search_term = incoming
        print directory
        ignore_tags=('script','noscript','style')
        #driver = webdriver.PhantomJS(self.phantom_js_executable)
        driver = webdriver.Chrome(self.webdriver_path)
        #driver.get(url)  # navigate to front page of each incentive program

        ##Navigate to "Installations" tab
        ## fixing for updates
        driver.get("http://arizonagoessolar.org/")
        time.sleep(5)
        driver.find_element_by_link_text("Utility Programs").click()
        time.sleep(3)
        driver.find_element_by_partial_link_text(search_term).click()
        time.sleep(5)
        driver.find_element_by_link_text("Installations").click()  # click on the "Installations" button to display installation records

        counter = 0
        morepages = True
        lastpage = False
        while morepages is True:  # while indicated that there are more pages to click through, continue function
            counter += 1
            content=driver.page_source
            cleaner=clean.Cleaner()
            content=cleaner.clean_html(content)
            doc=LH.fromstring(content)
            with open(os.path.join(self.text_file_output, directory, 'result' + str(counter) + '.txt'),'w') as f:  # directory and filename for text files
                for elt in doc.iterdescendants():  # write contents of page to text file
                    if elt.tag in ignore_tags: continue
                    text=elt.text or ''
                    tail=elt.tail or ''
                    words=' '.join((text,tail))#.strip()
                    if words:
                        words=words.encode('utf-8')
                        f.write(words+'\n')
            if nextlink is not None:
                if lastpage is True:  # if last page, continue to next incentive program or exit if no more programs available
                    morepages = False
                    continue
                try:
                    driver.find_element_by_link_text("Next").click()  # click on "next" button to go to next page
                    time.sleep(2)  # give chance for page to load
                    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, "Next")))  # since each page already has a "Next" button, this doesn't actually wait for new page to load - causing some duplication of extraction text files.
                except:
                    lastpage = True
                    message = traceback.format_exc()
                    print message
            else:
                morepages = False  # if nextlink not available, must be last page
        driver.close()




    def cleanFiles(self, incoming):
        """
        Scans through incentive program directory and deletes duplicate text files.
        Resulting number of files after this step should equal number of pages for each incentive program.
        """
        os.chdir(self.text_file_output + '%s' % incoming[2])
        removed_list = []
        for file in glob.glob('*.txt'):
            if file in removed_list:
                pass
            else:
                with open(file, 'r') as in_file:
                        fin = in_file.read()
                        for file2 in glob.glob('*.txt'):
                            if file != file2:
                                with open(file2,'r') as comp_in:
                                    comp = comp_in.read()
                                    if fin == comp:
                                        os.remove(file2)
                                        removed_list.append(file2)
                                        print incoming[2], file, file2
                            else:
                                pass


    def checkadditionalattributes(self, incoming):
        """
        Checks through all programs and searches for additional fields.
        This is optional, but should be ran each year to ensure new additional fields haven't been added.
        If additional fields have been added, will need to update consolidate() function to expect new additional field.
        """
        return_l = []
        os.chdir(self.text_file_output + '%s' % incoming[2])
        for file in glob.glob('*.txt'):
            with open(file,'r') as in_file:
                fin = in_file.read()
                finsplit = fin.split('[+]')
                for x in range(1,len(finsplit)):
                    finslice = finsplit[x].split('\n')
                    for y in range(0, len(finslice)):
                        if ':' in finslice[y]:
                            if finslice[y].split(':')[0].strip() in attributes_l:
                                continue
                            else:
                                return_l.append(finslice[y].split(':')[0].strip())
                        else:
                            pass
        return return_l


    def consolidate(self, url_info):
        """
        Consolidates all text files into single CSV.
        """
        def templatedict():
            mydict = collections.OrderedDict()
            mydict['utility'] = None
            mydict['status'] = None
            mydict['technology'] = None
            mydict['incentive_prog'] = None
            mydict['sys_size_kw'] = None
            mydict['power_gen'] = None
            mydict['system_cost'] = None
            mydict['incentive_offered'] = None
            mydict['zip_code'] = None
            mydict['app_date'] = None
            mydict['res_date'] = None
            mydict['install_date'] = None
            mydict['installer'] = None
            mydict['purchased_leased'] = None
            return mydict

        def firstrow():
            """Write header row to CSV"""
            first_row = ['Utility','Status','Technology','Incentive Program','System Size (kW)','Power Generation (kWh)','System Cost','Incentive Offered','Zip Code', 'Application Date','Reservation Date','Install Date','Installer','Purchased/Leased']
            return first_row

        with open(self.final_csv,'wb') as out_file:
            fout = csv.writer(out_file)
            fout.writerow(firstrow())
            for dir in url_info:
                directory = dir[2]
                os.chdir(self.text_file_output + '%s' % directory)
                for file in glob.glob('*.txt'):
                    with open (file, 'r') as in_file:
                        fin = in_file.read()
                        finsplit = fin.split('[+]')
                        #print('done')
                        for x in range(1,len(finsplit)):
                            mydict = templatedict()  # get template dictionary
                            finslice = finsplit[x].split('\n')
                            mydict['utility'] = dir[2].upper()
                            mydict['status'] = finslice[1].strip()
                            mydict['technology'] = finslice[3].strip()
                            mydict['incentive_prog'] = finslice[5].strip()
                            mydict['sys_size_kw'] = finslice[7].strip()
                            mydict['power_gen'] = finslice[9].strip()
                            mydict['system_cost'] = finslice[12].strip()
                            mydict['incentive_offered'] = finslice[15].strip()
                            mydict['zip_code'] = finslice[17].strip()
                            for item in finslice:
                                if 'Application Date:' in item:
                                    mydict['app_date'] = item.split(':')[1].strip()
                                elif 'Reservation Date:' in item:
                                    mydict['res_date'] = item.split(':')[1].strip()
                                elif 'Install Date:' in item:
                                    try:
                                        mydict['install_date'] = item.split(':')[1].strip()
                                    except:
                                        print file, item.split(':')
                                elif 'Installer:' in item:
                                    try:
                                        mydict['installer'] = item.split(':')[1].strip()
                                    except:
                                        print file, item.split(':')
                                elif 'Purchased' in item:
                                    mydict['purchased_leased'] = item.split(':')[1].strip()
                                else:
                                    pass
                            outrow = []
                            for k,v in mydict.iteritems():
                                outrow.append(v)
                            fout.writerow(outrow)



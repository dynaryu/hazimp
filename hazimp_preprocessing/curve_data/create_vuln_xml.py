"""
This is a script to convert curve info in other formats to NRML, v0.4.

It is being modified on a needs basis.


"""

import csv
import numpy

import xlrd
from core_hazimp.misc import csv2dict


def xml_write_variable(xml_h, name, value):
    """
    Add the variable name and value to an xml file.
    """
    xml_h.write('%s="' % name)
    try:
        xml_h.write(value)
    except (TypeError):
        if numpy.isnan(value):
            # This is what we need for blank sring values.
            # Probably not universal though.
            xml_h.write('')
        else:
            # to rethrow error
            xml_h.write(value)
    xml_h.write('" ')


def write_nrml_top(xml_h, vulnerability_set_id, asset_category, loss_category,
                   imt, imls):
    """
    Write the top section of an nrml file.
    """

    intro = """<?xml version='1.0' encoding='utf-8'?>
<nrml xmlns="http://openquake.org/xmlns/nrml/0.4"
      xmlns:gml="http://www.opengis.net/gml">

    <vulnerabilityModel>
        <config/>

        <discreteVulnerabilitySet """
    xml_h.write(intro)
    xml_write_variable(xml_h, "vulnerabilitySetID", vulnerability_set_id)
    xml_h.write('\n')
    xml_write_variable(xml_h, "assetCategory", asset_category)
    xml_write_variable(xml_h, "lossCategory", loss_category)
    xml_h.write('>\n <IML ')
    xml_write_variable(xml_h, "IMT", imt)
    xml_h.write('>')
    for iml in imls:
        if numpy.isnan(iml):
            continue
        xml_h.write(str(iml) + ' ')
    xml_h.write('</IML>\n')


def write_nrml_curve(xml_h, vulnerability_function_id, loss_ratio,
                     coef_var, alpha=None, beta=None):
    """
    Write the curve info of an nrml file.

    """
    xml_h.write("<discreteVulnerability ")
    xml_write_variable(xml_h, "vulnerabilityFunctionID",
                       vulnerability_function_id)
    if alpha is not None:
        xml_write_variable(xml_h, "Alpha", alpha)
    if beta is not None:
        xml_write_variable(xml_h, "Beta", beta)
    xml_h.write('')
    xml_h.write('probabilisticDistribution="LN">\n')
    xml_h.write('<lossRatio>')
    xml_h.write(loss_ratio)
    xml_h.write('</lossRatio>\n')
    xml_h.write('<coefficientsVariation>')
    xml_h.write(coef_var)
    xml_h.write('</coefficientsVariation>\n')
    xml_h.write('</discreteVulnerability>\n\n')


def write_nrml_close(xml_h):
    """
    Write the final section of an nrml file and close it.
    """
    xml_h.write('</discreteVulnerabilitySet>\n')
    xml_h.write('</vulnerabilityModel>\n')
    xml_h.write('</nrml>\n')
    xml_h.close()


def csv_curve2nrml(csv_filename, xml_filename):
    """
    Read in a csv hazard curve file and convert it to an NRML file.
    """
    # Read the file twice.
    # Once for the non-per-curve info and then
    # for the per curve info.

    csv_dict = csv2dict(csv_filename)
    vulnerability_set_id = csv_dict['vulnerabilitySetID'][0]
    try:
        asset_category = csv_dict['assetCategory'][0]
    except IndexError:
        # Assume asset_category is empty
        asset_category = ''
    loss_category = csv_dict['lossCategory'][0]
    imls = [v for v in csv_dict['IML'] if not v == '']

    # open the csv file to read the rows
    reader = csv.DictReader(open(csv_filename, 'rb'))
    xml_h = open(xml_filename, 'w')
    write_nrml_top(xml_h, vulnerability_set_id, asset_category, loss_category,
                   csv_dict['IMT'][0], imls)

    # Loop over the csv file info
    for row in reader:
        row = {k.strip(): v.strip() for k, v in row.iteritems()}
        if row['Alpha'] == 'N/A':
            # This row has no model
            continue
        coef_var = ''
        loss_ratio = ''
        for iml in imls:
            if numpy.isnan(iml):
                continue
            loss_ratio += str(row[str(int(iml))]) + ' '
            coef_var += '0 '
        write_nrml_curve(xml_h, row['vulnerabilityFunctionID'], loss_ratio,
                         coef_var, row['Alpha'], row['Beta'])
    write_nrml_close(xml_h)


def validate_excel_curve_data(excel_file):
    """
    Check that the titles and the water depths do not change
    from sheet to sheet.
    The first 2 rows are titles.
    The first coulmn is the water depth.
    """

    default = None
    valid = True
    titles = {}
    wb = xlrd.open_workbook(excel_file)
    for s in wb.sheets():
        title = []
        # The first 3 rows should be titles that are the same,
        # except for the 2nd value on the 1st row.
        for row in [0, 1, 2]:
            values = []
            for col in range(s.ncols):
                val = s.cell(row, col).value

                # This is just for visualising.
                try:
                    val = str(val)
                except TypeError:
                    pass

                values.append(val)
            title.append(values)
        # Remove the  2nd value on the 1st row.
        del title[0][1]
        titles[s.name] = title
        default = title

    if default is None:
        valid = False
    else:
        # Check that all sheets have the same title info
        for title in titles.values():
            if not title == default:
                print "title", title
                print "default", default
                valid = False
                break

    valid = check_identical_depths(wb, valid)
    return valid


def check_identical_depths(wb, valid):
    """
    Check that the depth values are the same for all workbooks.
    Check that the first colum, starting at the 4th row, is identical.
    """

    default = None
    depths = {}
    for s in wb.sheets():
        values = []
        for row in range(3, s.nrows):
            col = 0
            val = s.cell(row, col).value
            values.append(val)
        depths[s.name] = values
        default = values

    if default is None:
        valid = False
    else:
        # Check that all sheets have the same title info
        for depth in depths.values():
            if not depth == default:
                print "depth", depth
                print "default", default
                valid = False
                break

    return valid


def read_excel_curve_data(excel_file):
    """
    Read in the excel file info.  Specific, undocumented format.

    What info has to be in the return dict?

    vulnerability_set_id
     asset_category
      loss_category,
     csv_dict['IMT'][0], imls)
    """
    wb = xlrd.open_workbook(excel_file)
    a_sheet = wb.sheets()[0]

    # Get a list of the depths
    depths = []
    for row in range(3, a_sheet.nrows):
        col = 0
        val = a_sheet.cell(row, col).value
        depths.append(val)
    fabric_vuln_curves, contents_vuln_curves = read_excel_worksheet(wb)

    return depths, fabric_vuln_curves, contents_vuln_curves


def read_excel_worksheet(wb):
    """
    Read an excel worksheet


    """
    fabric_vuln_curves = {}  # the keys are curve names.
    contents_vuln_curves = {}  # the keys are curve names.

    for s in wb.sheets():
        di_block = []
        for row in range(3, s.nrows):
            values = []
            for col in range(s.ncols):
                values.append(s.cell(row, col).value)
            di_block.append(values)
        # Get individual curves from the curve block.
        # Convert the curves into an array
        di_array = numpy.asarray(di_block)
        insure = {"INSURED": 0, "UNINSURED": 4}
        for key in insure:
            # Read in the structure type
            # The 2nd value on the 1st row.
            curve_id_base = s.cell(0, 1).value.split()[0] + '_' + key
            fabric_vuln_curves[curve_id_base] = di_array[:, 1 + insure[key]]
            tag_offset = {'_SAVE': 2, '_NOACTION': 3, '_EXPOSE': 4}
            for tag in tag_offset:
                curve_id = curve_id_base + tag
                contents_vuln_curves[curve_id] = di_array[:, tag_offset[tag]
                                                          + insure[key]]
    return fabric_vuln_curves, contents_vuln_curves


FLOOD_HOUSE_FABRIC = 'structural_domestic_wind_2012'
FLOOD_HOUSE_CONTENTS = 'contents_domestic_wind_2012'
LOSS_CAT_FABRIC = 'structural_loss_ratio'
LOSS_CAT_CONTENTS = 'contents_loss_ratio'
FLOOD_IMT = 'water depth m'


def excel_curve2nrml(contents_filename, fabric_filename, xls_filename):
    """
    Read in an excel flood curve file and convert it to an NRML file.

    The excel file format is specific and best understood by looking
    at the file flood_2012_test.xlsx.
    """

    validate_excel_curve_data(xls_filename)

    depths, fabric_vuln_curves, contents_vuln_curves = read_excel_curve_data(
        xls_filename)
    curve_info = [{'curves': fabric_vuln_curves,
                   'set_id': FLOOD_HOUSE_FABRIC,
                   'asset': '',
                   'loss_category': LOSS_CAT_FABRIC,
                   'file_name': fabric_filename},
                  {'curves': contents_vuln_curves,
                   'set_id': FLOOD_HOUSE_CONTENTS,
                   'asset': '',
                   'loss_category': LOSS_CAT_CONTENTS,
                   'file_name': contents_filename}]

    for set_id in curve_info:

        xml_h = open(set_id['file_name'], 'w')
        write_nrml_top(xml_h, set_id['set_id'], set_id['asset'],
                       set_id['loss_category'],
                       FLOOD_IMT, depths)
        # Loop over the csv file info
        for curve_dic_key in set_id['curves']:
            curve_values = set_id['curves'][curve_dic_key]
            coef_var = ''
            loss_ratio = ''
            # creating the coef_var vector
            for iml in curve_values:
                loss_ratio += str(iml) + ' '
                coef_var += '0 '
            write_nrml_curve(xml_h, curve_dic_key, loss_ratio,
                             coef_var)
        write_nrml_close(xml_h)

#-----------------------------------------------------------
if __name__ == "__main__":
    # csv_curve2nrml('domestic_wind_vul_curves.csv',
    #               'domestic_wind_vul_curves.xml')
    excel_curve2nrml('content_flood_vul_curves.xml',
                     'fabric_flood_vul_curves.xml',
                     'Flood_2012_testb.xls')
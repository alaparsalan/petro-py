import sys
import os
import matplotlib.pyplot as plt

# Add the 'packages' folder to the Python path
packages_dir = os.path.join(os.getcwd(), 'packages')
sys.path.insert(0, packages_dir)

# Import petropy and lasio from the custom packages folder
import petropy as ptr

### 1. Read las file

# Create a Log object by reading a file path
las_file_path = r'examples\42303347740000.las'
log = ptr.Log(las_file_path)

### 2. Load tops

tops_file_path = 'tops.csv'
log.tops_from_csv(tops_file_path)

### 3. Graphically edit log

viewer = ptr.LogViewer(log, top=6950, height=100)
viewer.show(edit_mode=True)

# Overwrite log variable with updated log from LogViewer edits
log = viewer.log

### 4. Define formations

f = ['WFMPA', 'WFMPB', 'WFMPC']

### 5. Fluid properties

log.fluid_properties_parameters_from_csv()
log.formation_fluid_properties(f, parameter='WFMP')

### 6. Multimineral model

log.multimineral_parameters_from_csv()
log.formation_multimineral_model(f, parameter='WFMP')

### 7. Summations

c = ['OIP', 'BVH', 'PHIE']
log.summations(f, curves=c)

### 8. Pay flags

flag_1_gtoe = [('PHIE', 0.03)]
flag_2_gtoe = [('PAY_FLAG_1', 1), ('BVH', 0.02)]
flag_3_gtoe = [('PAY_FLAG_2', 1)]
flag_3_ltoe = [('SW', 0.2)]

log.add_pay_flag(f, greater_than_or_equal=flag_1_gtoe)
log.add_pay_flag(f, greater_than_or_equal=flag_2_gtoe)
log.add_pay_flag(f, greater_than_or_equal=flag_3_gtoe, less_than_or_equal=flag_3_ltoe)

### 9. Electrofacies

electro_logs = ['GR_N', 'RESDEEP_N', 'NPHI_N', 'RHOB_N', 'PE_N']
logs = [log]

logs = ptr.electrofacies(logs, f, electro_logs, 6, log_scale=['RESDEEP_N'])
log = logs[0]

### 10. Statistics

stats_curves = ['OIP', 'BVH', 'PHIE', 'SW', 'VCLAY', 'TOC']
log.statistics_to_csv('wfmp_statistics.csv', replace=True, formations=f, curves=stats_curves)

### 11. Export data

if len(log.well['WELL'].value) > 0:
    well_name = log.well['WELL'].value
elif len(str(log.well['UWI'].value)) > 0:
    well_name = str(log.well['UWI'].value)
elif len(log.well['API'].value) > 0:
    well_name = str(log.well['API'].value)
else:
    well_name = 'UNKNOWN'
well_name = well_name.replace('.', '')

wfmpa_top = log.tops['WFMPA']
wfmpc_base = log.next_formation_depth('WFMPC')

top = wfmpa_top
height = wfmpc_base - wfmpa_top

viewer = ptr.LogViewer(log, top=top, height=height, template_defaults='full_oil')
viewer.fig.set_size_inches(17, 11)
viewer.fig.suptitle(well_name, fontweight='bold', fontsize=30)

logo_im = plt.imread('company_logo.png')
logo_ax = viewer.fig.add_axes([0, 0.85, 0.2, 0.2])
logo_ax.imshow(logo_im)
logo_ax.axis('off')

if len(str(log.well['UWI'].value)) > 0:
    label = 'UWI: ' + str(log.well['UWI'].value) + '\n'
elif len(log.well['API'].value) > 0:
    label = 'API: ' + str(log.well['API'].value) + '\n'
else:
    label = ''

label += 'County: Reagan\nCreated By: Todd Heitmann\n'
label += 'Creation Date: October 23, 2017'
viewer.axes[0].annotate(label, xy=(0.99, 0.99), xycoords='figure fraction',
                        horizontalalignment='right', verticalalignment='top',
                        fontsize=14)

viewer_file_name = r'%s_processed.png' % well_name
las_file_name = r'%s_processed.las' % well_name

viewer.fig.savefig(viewer_file_name)
viewer.log.write(las_file_name)

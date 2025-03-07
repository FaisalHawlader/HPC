#Copy results from CV2X-B1 to YoGoKoBox (local machine)
scp -r root@CV2X-B1:/home/root/Ybox_results .

#Send the results to the HPC (iris-cluster) for further analysis
scp -r YoGoKoBox/Ybox_results fahawlader@iris-cluster:/work/projects/360lab/cv2x_vnc2024/Results

#Run the following command to capture the data from v2x0 interface and save it to a json file
tshark -i v2x0 >test.json

# Run the following to understand the use of the mwpubsub command
mwpubsub -h


# Check what its itsnet and CarGeo6 
itsnet -V

# Check the status of the itsnet service
systemctl status gn-itsnet


# Check the status of the AutotalksCr2V2X service that uses Gnss
mwconfig mib get-all -t AutotalksCr2Gnss
 
# Check the status of the AutotalksCr2V2X service that uses C-V2X 
mwconfig mib get-all -t AutotalksCr2CV2X

# Check the status of the PVT service
mwconfig mib get-all -t Pvt

# Change the read only file system to read write
mount -o remount,rw /

# Change the radio mode to v2x
echo -n "v2x" >/srv/nfs/atlk-cr2/etc/radio_mode

# Change back to read only file system
mount -o remount,ro /

# Check the status of the CaService that uses C-V2X
mwconfig mib get-all -t CaService

# Get management information base (MIB) of the AutotalksCr2V2X that uses C-V2X
 mwconfig mib get-all -t AutotalksCr2V2X
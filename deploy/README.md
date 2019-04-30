# Systemd Installation #

To run this as a systemd service, follow these simple instructions:

```bash
# Change to your source directory
cd ~/src

# Clone the repository
git clone git@github.com:gmfrasca/pointstreak-groupme.git
cd pointstreak-groupme

# Install requirements
pip install -Ur requirements.txt

# Update {{ HOME_DIRECTORY }}
vim deploy/psgroupme.service

# Make the service file read-only
chmod 444 deploy/psgroupme.service

# Copy to systemd folder
cp deploy/psgroupme.service /etc/systemd/system/psgroupme.service

# Start the service
sudo systemctl start psgroupme

# (Optional) Enable to run on startup
sudo systemctl enable psgroupme
```

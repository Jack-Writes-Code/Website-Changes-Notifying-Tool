# Website-Changes-Notifying-Tool
 
This script will monitor a list of websites and if the body of any of the websites change it will notify you via text (using ClickSend SMS API) and via email (requires SMTP details).

ClickSend SMS is NOT a free service, so you will need an account to utilise this.
You can use the SMTP email settings from your GMail if you don't have an SMTP email currently.

After detecting a change and notifying you, the script has a 30 minute 'cooldown' where it won't notify you about that site changing again until after that time period has passed. It will then notify you again on the next change.

You can monitor as many websites as you like. Please consider the computational power of the computer you're running the script on if you decide to monitor a lot of sites. Also please be aware of a websites policy against spam requests. Some websites don't allow scraping and won't allow a high volume of requests over an extended period of time.


Docker support is ready via Docker or Docker Compose.

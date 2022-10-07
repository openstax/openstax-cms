## Using DBBackup

 * Backups will be stored in this directory
 * To create a database backup run `python manage.py dbbackup`

## Copying backup to a different location

 * Log into the AWS CLI
 * run this command from bit-deployment
   * `bin/scp cms dev cron :~/www/cms/backup/[backup file name] ~/new/location`
   * Read more setup details in the scp file in bit-deployment
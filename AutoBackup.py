import os
import shutil
import time
import hashlib
import logging

from datetime import datetime

def setupLogger(logFile):
    logger = logging.getLogger('BackupLogger')
    logger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger

def getFileHash(filePath):
    hasher = hashlib.md5()
    with open(filePath, 'rb') as file:
        buff = file.read()
        hasher.update(buff)
    return hasher.hexdigest()

def syncFolders(sourceFolder, backupFolder, logger):
    print(f"Starting synchronization: {sourceFolder} -> {backupFolder}")
    changesMade = False

    # Create backup folder if it doesn't exist
    if not os.path.exists(backupFolder):
        os.makedirs(backupFolder)
        print(f"Created backup folder: {backupFolder}")
        logger.info(f"Created backup folder: {backupFolder}")
        changesMade = True

    # Walk through the source folder
    for root, dirs, files in os.walk(sourceFolder):
        print(f"Scanning directory: {root}")
        
        # Create corresponding subdirectories in backup folder
        relativePath = os.path.relpath(root, sourceFolder)
        backupPath = os.path.join(backupFolder, relativePath)
        if not os.path.exists(backupPath):
            os.makedirs(backupPath)
            print(f"Created directory: {backupPath}")
            logger.info(f"Created directory: {backupPath}")
            changesMade = True
        
        # Copy files
        for file in files:
            sourceFile = os.path.join(root, file)
            backupFile = os.path.join(backupPath, file)
            
            # Check if file needs to be updated
            if not os.path.exists(backupFile):
                shutil.copy2(sourceFile, backupFile)
                print(f"Added new file: {backupFile}")
                logger.info(f"Added new file: {backupFile}")
                changesMade = True
            else:
                sourceHash = getFileHash(sourceFile)
                backupHash = getFileHash(backupFile)
                if sourceHash != backupHash:
                    shutil.copy2(sourceFile, backupFile)
                    print(f"Updated file: {backupFile}")
                    logger.info(f"Updated file: {backupFile}")
                    changesMade = True
                else:
                    print(f"File up to date: {backupFile}")

    print("Checking for files to remove from backup...")
    for root, dirs, files in os.walk(backupFolder):
        relativePath = os.path.relpath(root, backupFolder)
        sourcePath = os.path.join(sourceFolder, relativePath)
        
        for dir in dirs[:]:
            if not os.path.exists(os.path.join(sourcePath, dir)):
                shutil.rmtree(os.path.join(root, dir))
                print(f"Removed directory: {os.path.join(root, dir)}")
                logger.info(f"Removed directory: {os.path.join(root, dir)}")
                dirs.remove(dir)
                changesMade = True
        
        for file in files:
            if not os.path.exists(os.path.join(sourcePath, file)):
                os.remove(os.path.join(root, file))
                print(f"Removed file: {os.path.join(root, file)}")
                logger.info(f"Removed file: {os.path.join(root, file)}")
                changesMade = True

    if changesMade:
        print("Changes were made during this sync process.")
        logger.info("Changes were made during this sync process.")
    else:
        print("No changes were necessary during this sync process.")
        logger.info("No changes were necessary during this sync process.")

    print("Sync process completed")
    return changesMade

# Example usage
sourceFolder = "E:\\sourceDir"
backupFolder = "E:\\backupDir"
logFile = "E:\\logFile\logs.txt"

logger = setupLogger(logFile)

while True:
    print("\n" + "="*50)
    print(f"Starting synchronization check at {datetime.now()}")
    print("="*50)
    logger.info("Starting synchronization check")
    changesMade = syncFolders(sourceFolder, backupFolder, logger)
    if changesMade:
        logger.info("Synchronized without changes")
        print(f"Synchronized with changes at {datetime.now()}")
    else:
        logger.info("Synchronized without changes")
        print(f"Synchronized with changes at {datetime.now()}")
    print(f"Waiting for 5 minutes before next sync check...")
    time.sleep(300)  # 5 minute delay between synchronization
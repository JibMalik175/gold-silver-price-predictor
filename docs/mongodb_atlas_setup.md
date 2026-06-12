# MongoDB Atlas Setup & Connection Guide

Follow these exact steps to create your database and connect it to your project.

## Step 1: Create a MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register).
2. Sign up for a free account.

## Step 2: Create a Cluster
1. After logging in, click **"Create"** to build a new deployment.
2. Select the **"M0" (Free)** tier.
3. Choose a provider (e.g., AWS) and a region (e.g., N. Virginia/us-east-1).
4. Click **"Create Deployment"**.

## Step 3: Set Up Security (Crucial)
1. **Database User**: 
   - Create a username (e.g., `admin`).
   - Create a password. **Save this password safely**; you will need it later.
   - Click **"Create Database User"**.
2. **IP Access List**:
   - Click **"Add My Current IP Address"** to allow your computer to connect.
   - (Optional for development) Click **"Allow Access from Anywhere"** (0.0.0.0/0) if you are working from different locations.
   - Click **"Finish and Close"**.

## Step 4: Get Your Connection String
1. Go to the **"Database"** tab in the sidebar.
2. Click the **"Connect"** button on your cluster.
3. Select **"Drivers"**.
4. Choose **Python** as the driver and select the latest version.
5. Copy the connection string. It will look like this:
   `mongodb+srv://<db_username>:<db_password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`

## Step 5: Configure Your Project
1. Open your project's `.env` file at: `f:\all projects\Silver\backend\.env`
2. Update the `MONGODB_URI` with the string you copied.
3. **Replace `<db_password>`** with the actual password you created in Step 3.
4. Set the `DB_NAME` (e.g., `silver_gold_db`).

### Example `.env` configuration:
```env
MONGODB_URI=mongodb+srv://admin:YourSecretPassword123@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=silver_gold_db
```

## Step 6: Verify the Connection
Run the migration script to test if the connection works:
1. Open a terminal in the `backend` folder.
2. Run:
   ```powershell
   python scripts/migrate_to_mongodb.py
   ```
   If successful, you will see "Finished migration" messages in the console.

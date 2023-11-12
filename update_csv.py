import pandas as pd

def update_csv(csv_file_path):
    # Load the CSV file into a DataFrame
    data = pd.read_csv(csv_file_path)

    # Add, update, or adjust columns as needed
    data['NewColumn'] = 'New Value'
    data.loc[data['ColumnName'] == 'ConditionValue', 'UpdatedColumn'] = 'New Value'
    data['ColumnToAdjust'] = data['ColumnToAdjust'].apply(lambda x: x * 2)

    # Save the updated DataFrame back to the CSV file
    data.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    # Replace 'path/to/your/csvfile.csv' with the actual path to your CSV file
    csv_file_path = 'C:\Users\User\Desktop\Wb_pro\soccer_prediction_system/soccer_data.csv'
    
    # Call the function to update the CSV file
    update_csv(csv_file_path)

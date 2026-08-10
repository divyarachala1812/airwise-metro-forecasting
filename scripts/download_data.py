from airwise.data import download_and_prepare

if __name__ == "__main__":
    frame = download_and_prepare()
    print(f"Prepared {len(frame):,} daily city records")

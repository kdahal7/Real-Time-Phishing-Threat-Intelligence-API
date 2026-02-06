"""
Generate Synthetic Phishing Dataset
Creates a dataset with both legitimate and phishing URLs for training
"""

import pandas as pd
import random
from typing import List
import os
from pathlib import Path


class DatasetGenerator:
    """Generate synthetic dataset for phishing detection"""
    
    # Legitimate domains
    LEGIT_DOMAINS = [
        'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
        'linkedin.com', 'amazon.com', 'microsoft.com', 'apple.com', 'github.com',
        'stackoverflow.com', 'reddit.com', 'wikipedia.org', 'medium.com', 'netflix.com',
        'spotify.com', 'dropbox.com', 'salesforce.com', 'adobe.com', 'cisco.com',
        'bing.com', 'yahoo.com', 'cnn.com', 'bbc.com', 'nytimes.com',
        'walmart.com', 'target.com', 'ebay.com', 'bestbuy.com', 'homedepot.com'
    ]
    
    # Suspicious/Phishing patterns
    PHISHING_KEYWORDS = [
        'login', 'signin', 'verify', 'account', 'update', 'confirm', 'secure',
        'banking', 'password', 'security', 'suspended', 'locked', 'urgent'
    ]
    
    SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club']
    
    @staticmethod
    def generate_legitimate_urls(n: int = 5000) -> List[str]:
        """Generate legitimate-looking URLs"""
        urls = []
        
        for _ in range(n):
            domain = random.choice(DatasetGenerator.LEGIT_DOMAINS)
            
            # Add variations
            variation = random.randint(1, 5)
            
            if variation == 1:
                # Simple homepage
                url = f"https://{domain}"
            elif variation == 2:
                # With path
                paths = ['about', 'contact', 'products', 'services', 'blog', 'news', 'help']
                url = f"https://{domain}/{random.choice(paths)}"
            elif variation == 3:
                # With subdomain
                subdomains = ['www', 'mail', 'blog', 'shop', 'support', 'dev', 'api']
                url = f"https://{random.choice(subdomains)}.{domain}"
            elif variation == 4:
                # With query parameters
                params = ['id', 'page', 'category', 'search', 'q']
                param = random.choice(params)
                value = random.randint(1, 100)
                url = f"https://{domain}/page?{param}={value}"
            else:
                # Complex path
                sections = ['products', 'category', 'items', 'details']
                section = random.choice(sections)
                item_id = random.randint(1000, 9999)
                url = f"https://{domain}/{section}/{item_id}"
            
            urls.append(url)
        
        return urls
    
    @staticmethod
    def generate_phishing_urls(n: int = 5000) -> List[str]:
        """Generate phishing-like URLs"""
        urls = []
        
        for _ in range(n):
            technique = random.randint(1, 10)
            
            if technique == 1:
                # IP address as domain
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                url = f"http://{ip}/{random.choice(DatasetGenerator.PHISHING_KEYWORDS)}"
            
            elif technique == 2:
                # Suspicious TLD
                domain = random.choice(DatasetGenerator.LEGIT_DOMAINS).replace('.com', '')
                tld = random.choice(DatasetGenerator.SUSPICIOUS_TLDS)
                keyword = random.choice(DatasetGenerator.PHISHING_KEYWORDS)
                url = f"http://{domain}-{keyword}{tld}"
            
            elif technique == 3:
                # @ symbol trick
                fake_domain = random.choice(DatasetGenerator.LEGIT_DOMAINS)
                real_evil = f"evil{random.randint(100,999)}.com"
                url = f"http://{fake_domain}@{real_evil}/{random.choice(DatasetGenerator.PHISHING_KEYWORDS)}"
            
            elif technique == 4:
                # Typosquatting
                domain = random.choice(DatasetGenerator.LEGIT_DOMAINS)
                # Insert typo
                typo_domain = domain.replace('o', '0').replace('l', '1').replace('a', 'а')
                keyword = random.choice(DatasetGenerator.PHISHING_KEYWORDS)
                url = f"http://{typo_domain}/{keyword}"
            
            elif technique == 5:
                # Subdomain overload
                legit = random.choice(DatasetGenerator.LEGIT_DOMAINS).replace('.com', '')
                evil_domain = f"evil{random.randint(100,999)}.com"
                keyword = random.choice(DatasetGenerator.PHISHING_KEYWORDS)
                url = f"http://{legit}.{keyword}.verify.{evil_domain}"
            
            elif technique == 6:
                # Long suspicious URL
                domain = f"secure-{random.choice(DatasetGenerator.LEGIT_DOMAINS).replace('.com', '')}"
                keywords = '-'.join(random.sample(DatasetGenerator.PHISHING_KEYWORDS, 3))
                url = f"http://{domain}-{keywords}-portal{random.randint(10,99)}.tk/login.php"
            
            elif technique == 7:
                # URL with excessive dots
                parts = [f"secure{random.randint(1,9)}", "account", "verify"]
                domain = f"evil{random.randint(100,999)}.com"
                url = f"http://{'.'.join(parts)}.{domain}"
            
            elif technique == 8:
                # Port number (suspicious)
                domain = random.choice(DatasetGenerator.LEGIT_DOMAINS).replace('.com', '') + str(random.randint(1,99))
                port = random.choice([8080, 8888, 3000, 8000])
                url = f"http://{domain}.tk:{port}/{random.choice(DatasetGenerator.PHISHING_KEYWORDS)}"
            
            elif technique == 9:
                # Suspicious path with many slashes
                domain = f"site{random.randint(100,999)}.xyz"
                path = '/'.join(['login', 'secure', 'verify', 'account', 'update'])
                url = f"http://{domain}/{path}"
            
            else:
                # Mixed suspicious elements
                legit_brand = random.choice(DatasetGenerator.LEGIT_DOMAINS).replace('.com', '')
                keyword = random.choice(DatasetGenerator.PHISHING_KEYWORDS)
                num = random.randint(100, 9999)
                url = f"http://{keyword}-{legit_brand}{num}.tk/secure/login.php?id={num}"
            
            urls.append(url)
        
        return urls
    
    @staticmethod
    def create_dataset(n_legitimate: int = 5000, n_phishing: int = 5000, output_path: str = None):
        """
        Create complete dataset with both legitimate and phishing URLs
        
        Args:
            n_legitimate: Number of legitimate URLs to generate
            n_phishing: Number of phishing URLs to generate
            output_path: Path to save the CSV file
        """
        print(f"Generating {n_legitimate} legitimate URLs...")
        legit_urls = DatasetGenerator.generate_legitimate_urls(n_legitimate)
        
        print(f"Generating {n_phishing} phishing URLs...")
        phishing_urls = DatasetGenerator.generate_phishing_urls(n_phishing)
        
        # Create dataframe
        df_legit = pd.DataFrame({
            'url': legit_urls,
            'label': 0  # 0 = Benign
        })
        
        df_phishing = pd.DataFrame({
            'url': phishing_urls,
            'label': 1  # 1 = Phishing
        })
        
        # Combine and shuffle
        df = pd.concat([df_legit, df_phishing], ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save to CSV
        if output_path is None:
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            output_path = data_dir / "phishing_dataset.csv"
        
        df.to_csv(output_path, index=False)
        print(f"\nDataset created successfully!")
        print(f"Total URLs: {len(df)}")
        print(f"Legitimate URLs: {len(df[df['label'] == 0])}")
        print(f"Phishing URLs: {len(df[df['label'] == 1])}")
        print(f"Saved to: {output_path}")
        
        return df


def main():
    """Main function to generate dataset"""
    print("=" * 60)
    print("Phishing URL Dataset Generator")
    print("=" * 60)
    
    # Generate dataset with 25,000 legitimate and 25,000 phishing URLs
    dataset = DatasetGenerator.create_dataset(
        n_legitimate=25000,
        n_phishing=25000
    )
    
    # Display sample
    print("\nSample URLs:")
    print("\nLegitimate URLs:")
    print(dataset[dataset['label'] == 0].head(5)['url'].to_string(index=False))
    
    print("\nPhishing URLs:")
    print(dataset[dataset['label'] == 1].head(5)['url'].to_string(index=False))


if __name__ == "__main__":
    main()

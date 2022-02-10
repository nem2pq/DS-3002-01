INSERT INTO `northwind_dw`.`dim_customers`
(`customer_key`,
`company`,
`last_name`,
`first_name`,
`job_title`,
`business_phone`,
`fax_number`,
`address`,
`city`,
`state_province`,
`zip_postal_code`,
`country_region`)
SELECT `id`,
`company`,
`last_name`,
`first_name`,
`job_title`,
`business_phone`,
`fax_number`,
`address`,
`city`,
`state_province`,
`zip_postal_code`,
`country_region`
FROM northwind.customers;

-- ----------------------------------------------
-- Validate that the Data was Inserted ----------
-- ----------------------------------------------
SELECT * FROM northwind_dw.dim_customers;


INSERT INTO `northwind_dw`.`dim_suppliers`
(`supplier_key`,
`company`,
`last_name`,
`first_name`,
`job_title`)
SELECT `id`,
`company`,
`last_name`,
`first_name`,
`job_title`
FROM northwind.suppliers;

-- ----------------------------------------------
-- Validate that the Data was Inserted ----------
-- ----------------------------------------------
SELECT * FROM northwind_dw.dim_suppliers;


-- ----------------------------------------------
-- TODO: Extract the appropriate data from 
--       the northwind database, and INSERT it
--       into the Northwind_DW database.
-- ----------------------------------------------
INSERT INTO `northwind_dw`.`dim_employees`
(`employee_key`,
`company`,
`last_name`,
`first_name`,
`email_address`,
`job_title`,
`business_phone`,
`home_phone`,
`fax_number`,
`address`,
`city`,
`state_province`,
`zip_postal_code`,
`country_region`,
`web_page`,
`notes`)
VALUES
(<{employee_key: }>,
<{company: }>,
<{last_name: }>,
<{first_name: }>,
<{email_address: }>,
<{job_title: }>,
<{business_phone: }>,
<{home_phone: }>,
<{fax_number: }>,
<{address: }>,
<{city: }>,
<{state_province: }>,
<{zip_postal_code: }>,
<{country_region: }>,
<{web_page: }>,
<{notes: }>);


-- ----------------------------------------------
-- Validate that the Data was Inserted ----------
-- ----------------------------------------------
SELECT * FROM northwind_dw.dim_employees;

INSERT INTO `northwind_dw`.`dim_shippers`
(`shipper_key`,
`company`,
`address`,
`city`,
`state_province`,
`zip_postal_code`,
`country_region`)
VALUES
(<{shipper_key: }>,
<{company: }>,
<{address: }>,
<{city: }>,
<{state_province: }>,
<{zip_postal_code: }>,
<{country_region: }>);

-- ----------------------------------------------
-- Validate that the Data was Inserted ----------
-- ----------------------------------------------
SELECT * FROM northwind_dw.dim_shippers;
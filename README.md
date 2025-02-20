<div align="center">
    <img alt="fossunited logo" src=".github/logo.png" width="150px" height="120px">
</div>

## The FOSS United Platform

Repo for the website and open-source platform of FOSS United. The whole platform is being built on [Frappe](https://frappe.io).

## Installation

- This project works the best on the latest Frappe Version v15. And is suggested to be installed on the same.
- Checkout Frappe Framework [Installation Docs](https://frappeframework.com/docs/) for setting up frappe on your [bench](https://frappeframework.com/docs/user/en/tutorial/install-and-setup-bench).
- If you encounter a password-related error after installing MariaDB while following the Frappe installation guide—despite not setting a password—follow [this DigitalOcean guide](https://www.digitalocean.com/community/tutorials/how-to-reset-your-mysql-or-mariadb-root-password) to reset the root password. If the `kill` command near the end of the article fails, find the MySQL processes using `ps aux | grep mysqld`, identify the `mysqld` and `mysql_safe` processes, and terminate them with `sudo kill -9 <pid>`. Verify that the processes are no longer running before proceeding.
- Create a new bench with
  `bench init fossu-bench`
- Clone the FOSS United Platform App.
  `bench get-app https://github.com/fossunited/fossunited`
- Create a [new site](https://frappeframework.com/docs/user/en/tutorial/create-a-site)
  `bench new-site test.localhost`
- Install the App on the created site
  `bench --site test.localhost install-app fossunited`
- Finally,
  `bench start`

Checkout [Access site in your browser](https://frappeframework.com/docs/user/en/tutorial/create-a-site#access-site-in-your-browser) for adding hosts.

### Steps to install and run the [FOSS United Dashboard](https://fossunited.org/dashboard)

The FOSS United Dashboard is a centralised admin UI for all the users signed up on fossunited.org. The Dashboard provides volunteers with the feature to manage all of the activities happening in their FOSS Club or City Chapter. Here are the steps to install and get the dashboard going:

- The code for dashboard is located under `fossunited/dashboard`.
- Install and Build the dashboard with `yarn install`.
- Run the dashboard in the root directory of the project with `yarn dev`.
- Add "ignore_csrf": 1 to your `common_site_config.json.`
- Dashboard will now be accessible on `<sitename>:8080`.

## Pre-commit

For automatic running of linters before you commit:

```
$ pip install pre-commit
$ pre-commit install
```

### Contribution

Want to contribute to the platform ? Checkout the [contribution guidelines](/CONTRIBUTING.md).

### Security Policy

Please checkout [Security Policy](/SECURITY.md) for information about reporting a Security Bug or Vulnerability.

## License

The repository has been released under [AGPL-3.0](https://github.com/fossunited/fossunited/blob/develop/LICENSE).
By Contributing to the FOSS United Platform, you agree that all your contributions will be licensed under AGPL License.

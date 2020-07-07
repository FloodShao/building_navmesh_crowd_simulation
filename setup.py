from setuptools import setup

package_name = 'building_navmesh_tools'

setup(
    name=package_name,
    version='0.0.0',
    packages=[
        'building_navmesh',
        'navmesh_generator'
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fred',
    maintainer_email='fred.guoliang.shao@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)

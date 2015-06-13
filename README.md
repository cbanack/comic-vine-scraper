### Docs and Binaries

All documentation about this project, including the latest downloads and installation instructions
can be found on the Comic Vine Scraper [Wiki page](https://github.com/cbanack/comic-vine-scraper/wiki/Introduction).

### Technical Details

This project is written for Windows, using IronPython and the .NET library.  It displays WinForms graphics and make 
heavy use of the [ComicVine RESTful API](http://www.comicvine.com/api/).  It is a _plugin_ for the
[ComicRack](http://comicrack.cyolito.com/) comic book reader, which is a standalone Windows desktop application.
Except during development (see below), Comic Vine Scraper does _not_ run outside of ComicRack's plugin environment.   

This project's repository is configured to compile and run in the [Eclipse IDE](https://eclipse.org/) using the
[Aptana Pydev](http://pydev.org/) plugin with IronPython correctly installed and configured.

### Pull Requests

At this point, I am not accepting pull requests.  Comic Vine Scraper is a stable, mature project and most of 
the work on it these days is maintenance and bug fixing.  I may accept well-written pull requests for clear, 
unambiguous bug fixes, but _please contact me_ before you begin doing any significant amount of work.

### License 

This project is created and distributed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).
This is an open source license, so you are welcome to create, build, and maintain your own fork of the codebase
if you have a major enhancement that  you want to add, or a wild new direction that you'd like to take 
the project.

    Unless required by applicable law or agreed to in writing, software 
    distributed under this License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

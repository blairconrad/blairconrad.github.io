namespace DataTableExample
{
    using System;
    using System.IO;
    using System.Linq;

    static class Program
    {
        static void Main()
        {
            var library = new LibraryBooks();

            const string booksXml = @"
<LibraryBooks xmlns='http://tempuri.org/LibraryBooks.xsd'>
  <Books>
    <Title>Zen Shorts</Title>
    <DueDate>2015-10-24T00:00:00-04:00</DueDate>
  </Books>
</LibraryBooks>";

            using (var reader = new StringReader(booksXml))
            {
                library.ReadXml(reader);
            }
            library.AcceptChanges();

            var books = library.Books;

            Console.Out.WriteLine("0th book's Library:\t{0}", books[0].Library);
            Console.Out.WriteLine("# WPL books by Select:\t{0}", library.Books.Select("Library = 'WPL'").Length);
            Console.Out.WriteLine("# WPL books by LINQ:\t{0}", library.Books.Count(book => book.Library == "WPL"));
        }
    }
}
